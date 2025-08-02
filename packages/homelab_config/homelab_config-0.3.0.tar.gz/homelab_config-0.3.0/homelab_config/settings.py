"""Settings module for Homelab configuration management.

This module defines the configuration settings and environment types for the Homelab
configuration system. It uses Pydantic for settings management and validation.

The settings can be configured through environment variables with the prefix 'HOMELAB_'.

Typical usage example:

    from homelab_config.settings import HomelabSettings, EnvironmentType

    # Create settings with environment variables
    settings = HomelabSettings()

    # Create settings with explicit values
    settings = HomelabSettings(
        environment=EnvironmentType.DEV,
        consul_urls="http://localhost:8500"
    )
"""

from enum import Enum

from pydantic import Field
from pydantic import SecretStr
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from homelab_config.utils import parse_consul_url
from homelab_config.utils import parse_consul_urls


class EnvironmentType(str, Enum):
    """Environment types supported by the system.

    Defines the valid environment types that can be used for configuration management.
    Each environment represents a different deployment context.
    """

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class HomelabSettings(BaseSettings):
    """Settings for Homelab configuration management.

    This class defines all configurable settings for the Homelab system.
    It uses Pydantic for validation and environment variable parsing.

    All settings can be configured through environment variables with the prefix 'HOMELAB_'.
    Example: HOMELAB_ENVIRONMENT=dev

    Attributes:
        environment: The current environment type (dev/staging/prod)
        consul_urls: List of Consul server URLs in priority order
        consul_token: Optional authentication token for Consul
        consul_cache_ttl: Cache duration for Consul client connections
    """

    model_config = SettingsConfigDict(
        env_prefix="HOMELAB_",
        case_sensitive=False,
        validate_assignment=True,
        use_enum_values=True,
        extra="ignore",
    )

    environment: EnvironmentType = Field(
        default=EnvironmentType.PROD, description="Runtime environment (dev/staging/prod)"
    )

    consul_urls: str | list[str] = Field(
        ...,  # Required field
        description="Comma-separated list of Consul server URLs in priority order",
    )

    consul_token: SecretStr | None = Field(default=None, description="Optional authentication token for Consul")

    consul_cache_ttl: int = Field(
        default=300, description="Cache duration for Consul client connections in seconds (default: 300)"
    )

    @field_validator("consul_urls", mode="before")
    @classmethod
    def validate_consul_urls(cls, v: str | list[str] | SecretStr) -> list[str]:
        """Validate and normalize Consul URLs.

        Args:
            v: Raw URL input from environment or constructor

        Returns:
            list[str]: List of validated Consul URLs

        Raises:
            ValueError: If any URL is invalid or no valid URLs are provided
        """
        urls = parse_consul_urls(v)
        if not urls:
            raise ValueError("At least one valid Consul URL must be provided")

        # Validate each URL individually
        validated_urls = []
        for url in urls:
            try:
                # Verify the URL can be parsed properly
                parse_consul_url(url)
                validated_urls.append(url)
            except ValueError as e:
                raise ValueError(f"Invalid Consul URL '{url}': {e!s}") from e

        return validated_urls
