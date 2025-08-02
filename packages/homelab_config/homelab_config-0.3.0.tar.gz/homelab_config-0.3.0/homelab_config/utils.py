"""Utility module for Homelab configuration management.

This module provides utility functions for handling URLs, secret values,
and other common operations used in the Homelab configuration system.
"""

import json

import hcl2
import xmltodict
import yaml
from loguru import logger
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


def load_yaml(content: str) -> dict:
    """Parse YAML content into a Python dictionary.

    Args:
        content: YAML formatted string

    Returns:
        dict: Parsed YAML content

    Raises:
        ValueError: If the YAML content is invalid or cannot be parsed
    """
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML content: {e!s}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse YAML: {e!s}") from e


def load_json(content: str) -> dict:
    """Parse JSON content into a Python dictionary.

    Args:
        content: JSON formatted string

    Returns:
        dict: Parsed JSON content

    Raises:
        ValueError: If the JSON content is invalid or cannot be parsed
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e!s}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e!s}") from e


def load_hcl(content: str) -> dict:
    """Parse HCL (HashiCorp Configuration Language) content into a Python dictionary.

    Args:
        content: HCL formatted string

    Returns:
        dict: Parsed HCL content

    Raises:
        ValueError: If the HCL content is invalid or cannot be parsed
    """
    try:
        return hcl2.loads(content)
    except Exception as e:
        raise ValueError(f"Failed to parse HCL: {e!s}") from e


def load_xml(content: str) -> dict:
    """Parse XML content into a Python dictionary.

    Args:
        content: XML formatted string

    Returns:
        dict: Parsed XML content

    Raises:
        ValueError: If the XML content is invalid or cannot be parsed

    Note:
        This function uses xmltodict to convert XML to a dictionary format.
        XML attributes will be prefixed with '@' in the resulting dictionary.
    """
    try:
        return xmltodict.parse(content)
    except Exception as e:
        raise ValueError(f"Failed to parse XML: {e!s}") from e


def load_content(content: str, format: str | None = None) -> dict:
    """Load content string into a Python dictionary.

    Args:
        content: The content string to parse
        format: Optional format specification ('json', 'yaml', 'hcl', 'xml')
               If specified, only try this format
               If None, try all formats in order: yaml -> json -> hcl -> xml

    Returns:
        dict: Parsed content as a Python dictionary

    Raises:
        ValueError: If content cannot be parsed with any supported format,
                   or if specified format is not supported
    """
    if not content or not content.strip():
        return {}

    # 定义支持的格式及其加载函数，按优先级排序
    loaders = {
        "yaml": load_yaml,  # 最常用的格式其次
        "json": load_json,  # 最严格的格式优先
        "hcl": load_hcl,  # 特定领域格式
        "xml": load_xml,  # 最后尝试
    }

    # 如果指定了格式
    if format:
        format = format.lower()
        if format not in loaders:
            raise ValueError(f"Unsupported format: {format}. Available formats: {', '.join(loaders.keys())}")
        try:
            return loaders[format](content)
        except Exception as e:
            raise ValueError(f"Failed to parse content as {format}: {e!s}") from e

    # 如果没有指定格式，依次尝试所有格式
    last_error = None
    for fmt, loader in loaders.items():
        try:
            result = loader(content)
            logger.debug(f"Successfully parsed content as {fmt}")
            return result
        except Exception as e:
            last_error = e
            continue

    raise ValueError(f"Failed to parse content in any supported format. Last error: {last_error!s}")
