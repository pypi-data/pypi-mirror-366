"""Utility module for Homelab configuration management.

This module provides utility functions for handling URLs, secret values,
and other common operations used in the Homelab configuration system.
"""

from pydantic import SecretStr
from yarl import URL


def unwrap_secret(value: str | SecretStr) -> str:
    """Safely unwrap a value that might be a SecretStr.

    Args:
        value: A string or SecretStr value to unwrap

    Returns:
        str: The unwrapped string value
    """
    return value.get_secret_value() if isinstance(value, SecretStr) else value


def split_url_list(urls: str) -> list[str]:
    """Split a comma-separated URL string into a list of URLs.

    Handles whitespace and empty entries properly.

    Args:
        urls: A comma-separated string of URLs

    Returns:
        list[str]: List of cleaned and validated URLs

    Example:
        >>> split_url_list("http://example.com, https://backup.com")
        ['http://example.com', 'https://backup.com']
    """
    if not urls:
        return []
    return [url.strip() for url in urls.split(",") if url.strip()]


def parse_consul_urls(urls: str | SecretStr | list[str | SecretStr] | None) -> list[str]:
    """Parse and normalize Consul server URLs from various input formats.

    Args:
        urls: URLs in any supported format

    Returns:
        list[str]: List of normalized URLs
    """
    if urls is None:
        return []

    if isinstance(urls, str | SecretStr):
        value = unwrap_secret(urls)
        # Handle potential newlines or other whitespace in the input
        value = value.replace("\n", ",").replace("\r", ",")
        return split_url_list(value)

    if isinstance(urls, list):
        result = []
        for item in urls:
            if isinstance(item, str | SecretStr):
                result.extend(parse_consul_urls(item))
        return result

    return []


def parse_consul_url(url: str) -> dict[str, str | int]:
    """Parse and validate a single Consul URL.

    Args:
        url: A single Consul server URL

    Returns:
        dict: Parsed URL components containing:
            - host: Server hostname
            - port: Server port number
            - scheme: URL scheme (http/https)

    Raises:
        ValueError: If the URL is invalid or malformed
    """
    try:
        # 预处理 URL，移除多余的空白
        url = url.strip()
        parsed = URL(url)

        if not parsed.host:
            raise ValueError("Missing host") from None
        scheme = parsed.scheme or "http"
        default_port = 443 if scheme == "https" else 8500
        if parsed.port is not None:
            try:
                port = int(parsed.port)
            except ValueError as err:
                raise ValueError("Invalid port number") from err
        else:
            port = default_port

        return {"host": parsed.host, "port": port, "scheme": scheme}
    except Exception as err:
        raise ValueError(f"URL parsing failed: {err!s}") from err
