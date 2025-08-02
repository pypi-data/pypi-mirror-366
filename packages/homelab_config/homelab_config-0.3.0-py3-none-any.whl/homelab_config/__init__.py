"""Homelab Configuration Management Package.

This package provides tools and utilities for managing configuration through Consul
in a homelab environment. It includes client interfaces, caching mechanisms,
and environment-aware configuration management.

Typical usage example:

    from homelab_config import HomelabClient, create_client

    # Create a client with default settings
    client = create_client()

    # Get configuration values
    dev_config = client("app/myconfig,dev")
    prod_config = client("app/myconfig,prod")
"""

from homelab_config.cached import consul_cached
from homelab_config.core import HomelabClient
from homelab_config.core import create_client
from homelab_config.settings import EnvironmentType
from homelab_config.settings import HomelabSettings


__author__ = "Shawn Deng"
__email__ = "shawndeng1109@qq.com"
__version__ = "0.1.0"

__all__ = [
    "EnvironmentType",
    "HomelabClient",
    "HomelabSettings",
    "consul_cached",
    "create_client",
]
