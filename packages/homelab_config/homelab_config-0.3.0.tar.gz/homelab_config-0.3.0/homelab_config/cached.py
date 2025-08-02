"""Cache module for Homelab configuration management.

This module provides caching functionality for Consul connections,
implementing a TTL-based caching strategy with connection validation.
"""

import os
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any
from typing import TypeVar

from diskcache import Cache
from loguru import logger


T = TypeVar("T")

# 缓存初始化
cache_dir = os.path.join(tempfile.gettempdir(), "homelab_consul_cache")
logger.debug("Initializing consul cache directory: {}", cache_dir)
_cache = Cache(directory=cache_dir)


@dataclass
class CacheEntry:
    """Represents a cached item with its metadata.

    Attributes:
        key: The cache key for the item
        timestamp_key: The cache key for the timestamp
        value: The cached value
        timestamp: The time when the item was cached
        ttl: Time-to-live in seconds
    """

    key: str
    timestamp_key: str
    value: Any
    timestamp: float
    ttl: int

    @property
    def age(self) -> int:
        """Get the age of the cached item in seconds."""
        return int(time.time() - self.timestamp)

    @property
    def remaining_ttl(self) -> int:
        """Get the remaining TTL in seconds."""
        return max(0, self.ttl - self.age)

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return self.age > self.ttl


class ConsulCache:
    """Handles caching operations for Consul connections."""

    @staticmethod
    def create_cache_keys(func: Callable, args: tuple, kwargs: dict) -> tuple[str, str]:
        """Create cache keys for a function call.

        Args:
            func: The function being cached
            args: Function arguments
            kwargs: Function keyword arguments

        Returns:
            tuple: (cache_key, timestamp_key)
        """
        cache_key = f"{func.__name__}:{args!s}:{kwargs!s}"
        timestamp_key = f"{cache_key}:timestamp"
        return cache_key, timestamp_key

    @staticmethod
    def get_entry(cache_key: str, timestamp_key: str, ttl: int) -> CacheEntry | None:
        """Retrieve a cache entry if it exists.

        Args:
            cache_key: Key for the cached value
            timestamp_key: Key for the timestamp
            ttl: Time-to-live in seconds

        Returns:
            Optional[CacheEntry]: The cache entry if found and valid, None otherwise
        """
        value = _cache.get(cache_key)
        timestamp = _cache.get(timestamp_key)

        if value is None or timestamp is None:
            return None

        return CacheEntry(key=cache_key, timestamp_key=timestamp_key, value=value, timestamp=timestamp, ttl=ttl)

    @staticmethod
    def save_entry(entry: CacheEntry) -> None:
        """Save a cache entry.

        Args:
            entry: The cache entry to save
        """
        _cache.set(entry.key, entry.value)
        _cache.set(entry.timestamp_key, entry.timestamp)
        logger.debug("Saved new cache entry (TTL: {}s)", entry.ttl)

    @staticmethod
    def validate_consul_connection(client: Any) -> bool:
        """Validate a cached Consul connection.

        Args:
            client: Consul client to validate

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            client.status.leader()
            return True
        except Exception as err:
            logger.warning("Cached connection is invalid: {!s}", err)
            return False


def consul_cached(ttl: int | Callable[..., int]):
    """Decorator for caching Consul connections with TTL.

    Args:
        ttl: Time-to-live in seconds or a function that returns TTL
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 计算实际的 TTL 值
            actual_ttl = ttl(*args) if callable(ttl) else ttl

            # 获取缓存键
            cache_key, timestamp_key = ConsulCache.create_cache_keys(func, args, kwargs)

            # 尝试获取缓存条目
            entry = ConsulCache.get_entry(cache_key, timestamp_key, actual_ttl)

            # 检查缓存是否有效
            if entry and not entry.is_expired and ConsulCache.validate_consul_connection(entry.value):
                logger.info("Using cached connection (age: {}s, expires in: {}s)", entry.age, entry.remaining_ttl)
                return entry.value

            # 创建新连接
            logger.info("Creating new connection")
            client = func(*args, **kwargs)

            # 保存到缓存
            new_entry = CacheEntry(
                key=cache_key, timestamp_key=timestamp_key, value=client, timestamp=time.time(), ttl=actual_ttl
            )
            ConsulCache.save_entry(new_entry)

            return client

        return wrapper

    return decorator
