"""Core module for Homelab configuration management.

This module provides the main client interface for interacting with Consul-based
configuration management in a homelab environment. It handles connection management,
environment-aware configuration retrieval, and connection caching.

Typical usage example:

    client = create_client()

    # Get config using default environment
    config = client("app/myapp/config")

    # Get config with specific environment
    prod_config = client("app/myapp/config,prod")
"""

from consul import Consul
from consul import ConsulException
from loguru import logger
from pydantic import SecretStr

from homelab_config.cached import consul_cached
from homelab_config.settings import EnvironmentType
from homelab_config.settings import HomelabSettings
from homelab_config.utils import load_content
from homelab_config.utils import parse_consul_url


class HomelabClient:
    """A client for managing homelab configuration through Consul.

    This client provides an interface to interact with Consul key-value store,
    handling connection management, caching, and environment-specific configuration.

    Attributes:
        settings: The configuration settings for the client
        cache_ttl: Time-to-live for cached connections in seconds
    """

    def __init__(
        self,
        consul_urls: list[str] | str | SecretStr | None = None,
        consul_token: str | SecretStr | None = None,
        settings: HomelabSettings | None = None,
        cache_ttl: int | None = None,
    ) -> None:
        """Initialize the HomelabClient.

        Args:
            consul_urls: URLs for Consul servers. Can be a single URL or a list.
            consul_token: Authentication token for Consul.
            settings: Custom settings instance. If not provided, will create from other params.
            cache_ttl: Custom cache duration in seconds. Overrides settings value.
        """
        self.settings = settings or self._build_config(consul_urls, consul_token)
        self._consul: Consul | None = None
        self.cache_ttl = cache_ttl if cache_ttl is not None else self.settings.consul_cache_ttl

    def _build_config(
        self,
        consul_urls: list[str] | str | SecretStr | None = None,
        consul_token: str | SecretStr | None = None,
    ) -> HomelabSettings:
        """Build configuration from provided parameters.

        Args:
            consul_urls: URLs for Consul servers. If None, will try to load from environment.
            consul_token: Authentication token for Consul. If None, will try to load from environment.

        Returns:
            HomelabSettings: Constructed settings object

        Note:
            If neither consul_urls parameter nor HOMELAB_CONSUL_URLS environment variable is set,
            HomelabSettings will raise a ValidationError.
        """
        logger.debug("Initializing HomelabSettings configuration")
        settings_kwargs = {}

        if consul_urls:
            logger.debug("Setting consul URLs from parameters")
            settings_kwargs["consul_urls"] = consul_urls

        if consul_token:
            logger.debug("Setting consul token from parameters")
            settings_kwargs["consul_token"] = (
                consul_token if isinstance(consul_token, SecretStr) else SecretStr(consul_token)
            )

        # HomelabSettings 会自动从环境变量加载配置
        logger.debug("Creating HomelabSettings (will load from env if params not provided)")
        config = HomelabSettings(**settings_kwargs)

        return config

    def _create_consul_client(self) -> Consul:
        logger.info("Creating new Consul client")
        last_error = None

        for url in self.settings.consul_urls:
            url_info = parse_consul_url(url)
            host = url_info.get("host", "unknown")
            port = url_info.get("port", "unknown")

            logger.debug("Attempting to connect to Consul at {}:{}", host, port)

            try:
                client = Consul(
                    **url_info,
                    token=self.settings.consul_token.get_secret_value(),
                )
                client.status.leader()
                logger.info("Successfully connected to Consul at {}:{}", host, port)
                return client

            except Exception as e:
                logger.warning("Failed to connect to Consul at {}:{}: {!s}", host, port, e)
                last_error = e
                continue

        if last_error:
            error_msg = f"Failed to connect to any Consul server. Last error: {last_error!s}"
            logger.error(error_msg)
            raise ConsulException(error_msg)

        error_msg = "No Consul URLs provided"
        logger.error(error_msg)
        raise ConsulException(error_msg)

    @property
    @consul_cached(ttl=lambda self, *args: self.cache_ttl)  # 修改这里
    def consul(self) -> Consul:
        if not self._consul:
            self._consul = self._create_consul_client()
        return self._consul

    def _validate_environment(self, env: str) -> bool:
        """Validate if the environment type is legal.

        Args:
            env: Environment type string to validate

        Returns:
            bool: True if environment is valid, False otherwise
        """
        try:
            EnvironmentType(env.lower())
            return True
        except ValueError:
            return False

    def _get_full_key(self, key: str) -> str:
        """Get the full configuration key with environment.

        Args:
            key: Base configuration key

        Returns:
            str: Full configuration key with environment

        Raises:
            ValueError: If the specified environment is invalid
        """
        if "," in key:
            base_key, env = key.rsplit(",", 1)
            if not self._validate_environment(env):
                valid_envs = [e.value for e in EnvironmentType]
                raise ValueError(f"Invalid environment type: {env}. Must be one of: {', '.join(valid_envs)}")
            return f"{base_key},{env.lower()}"
        return f"{key},{self.settings.environment}"

    def __call__(self, key: str, format: str | None = "yaml") -> dict | str | None:
        """Get configuration value for the given key.

        The key can include an environment suffix (e.g., 'app/config,prod').
        If no environment is specified, the default environment from settings is used.

        Args:
            key: Configuration key, optionally with environment suffix
            format: Optional format specification ('yaml', 'json', 'hcl', 'xml')
                   If not provided, will try to parse as YAML first, then other formats

        Returns:
            Union[dict, str, None]:
                - dict: If content was successfully parsed as structured data
                - str: If parsing failed
                - None: If key doesn't exist

        Raises:
            ValueError: If specified environment is invalid
            ConsulException: If connection to Consul fails
        """
        # 1. 处理环境并获取完整键名
        full_key = self._get_full_key(key)  # 可能抛出 ValueError
        logger.debug("Fetching config for key: {} (full key: {})", key, full_key)

        # 2. 从 Consul 获取数据
        _, data = self.consul.kv.get(full_key)
        if not data or "Value" not in data:
            return None

        content = data["Value"].decode("utf-8")
        try:
            return load_content(content, format=format)
        except ValueError as e:
            logger.debug("Failed to parse content as structured data: {}", str(e))
            return content


def create_client(
    consul_urls: list[str] | str | SecretStr | None = None,
    consul_token: str | SecretStr | None = None,
    settings: HomelabSettings | None = None,
    cache_ttl: int | None = None,
) -> HomelabClient:
    """Create a new HomelabClient instance.

    This is the recommended way to instantiate a HomelabClient.

    Args:
        consul_urls: URLs for Consul servers
        consul_token: Authentication token for Consul
        settings: Custom settings instance
        cache_ttl: Custom cache duration in seconds

    Returns:
        HomelabClient: Configured client instance
    """
    return HomelabClient(consul_urls=consul_urls, consul_token=consul_token, settings=settings, cache_ttl=cache_ttl)


# Usage example
if __name__ == "__main__":
    client = create_client()

    try:
        # 1. 使用默认环境，自动尝试解析为 YAML
        config = client("cfg/tmp/tmp")
        print("Default environment config:", config)

        # 2. 显式指定不同格式
        yaml_config = client("cfg/tmp/tmp", format="yaml")
        print(yaml_config)

        _config = client("cfg/tmp/tmp")
        print(_config)

    except ValueError as e:
        print(f"Error: {e}")
