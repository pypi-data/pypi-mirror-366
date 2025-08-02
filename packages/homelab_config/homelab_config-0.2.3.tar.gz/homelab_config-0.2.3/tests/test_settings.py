"""Tests for settings module."""

import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr
from pydantic import ValidationError

from homelab_config.settings import EnvironmentType
from homelab_config.settings import HomelabSettings


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test.

    This fixture runs automatically before each test to ensure no environment
    variables interfere with the tests.
    """
    # 保存原始环境变量
    original_env = dict(os.environ)

    # 删除所有 HOMELAB_ 相关的环境变量
    for key in list(os.environ.keys()):
        if key.startswith("HOMELAB_"):
            del os.environ[key]

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


def test_environment_type_values():
    """Test EnvironmentType enum values."""
    assert EnvironmentType.DEV == "dev"
    assert EnvironmentType.STAGING == "staging"
    assert EnvironmentType.PROD == "prod"


def test_default_settings():
    """Test default settings values."""
    settings = HomelabSettings(consul_urls="http://localhost:8500")
    assert settings.environment == EnvironmentType.PROD
    assert settings.consul_urls == ["http://localhost:8500"]
    assert settings.consul_token is None
    assert settings.consul_cache_ttl == 300


@pytest.mark.parametrize(
    "consul_urls,expected",
    [
        ("http://localhost:8500", ["http://localhost:8500"]),
        (
            "http://consul1:8500,http://consul2:8500",
            ["http://consul1:8500", "http://consul2:8500"],
        ),
        (["http://localhost:8500"], ["http://localhost:8500"]),
        (
            [SecretStr("http://consul1:8500"), "http://consul2:8500"],
            ["http://consul1:8500", "http://consul2:8500"],
        ),
    ],
)
def test_valid_consul_urls(consul_urls, expected):
    """Test valid Consul URL configurations."""
    settings = HomelabSettings(consul_urls=consul_urls)
    assert settings.consul_urls == expected


@pytest.mark.parametrize(
    "consul_urls,error_pattern",
    [
        ("", "At least one valid Consul URL must be provided"),
        ("invalid_url", "URL parsing failed"),
        (["invalid_url"], "Invalid Consul URL"),
        ("http://consul1:invalid", "URL parsing failed"),
    ],
)
def test_invalid_consul_urls(consul_urls, error_pattern):
    """Test invalid Consul URL configurations."""
    with pytest.raises(ValidationError) as exc_info:
        HomelabSettings(consul_urls=consul_urls)
    assert error_pattern in str(exc_info.value)


def test_consul_token_handling():
    """Test Consul token handling."""
    # Test with plain string token
    settings = HomelabSettings(
        consul_urls="http://localhost:8500",
        consul_token="secret_token",
    )
    assert isinstance(settings.consul_token, SecretStr)
    assert settings.consul_token.get_secret_value() == "secret_token"

    # Test with SecretStr token
    settings = HomelabSettings(
        consul_urls="http://localhost:8500",
        consul_token=SecretStr("secret_token"),
    )
    assert isinstance(settings.consul_token, SecretStr)
    assert settings.consul_token.get_secret_value() == "secret_token"


@pytest.mark.parametrize(
    "env_vars,expected",
    [
        (
            {
                "HOMELAB_ENVIRONMENT": "dev",
                "HOMELAB_CONSUL_URLS": "http://consul1:8500,http://consul2:8500",
                "HOMELAB_CONSUL_TOKEN": "test_token",
                "HOMELAB_CONSUL_CACHE_TTL": "600",
            },
            {
                "environment": EnvironmentType.DEV,
                "consul_urls": ["http://consul1:8500", "http://consul2:8500"],
                "consul_token": "test_token",
                "consul_cache_ttl": 600,
            },
        ),
        (
            {
                "HOMELAB_ENVIRONMENT": "staging",
                "HOMELAB_CONSUL_URLS": "http://localhost:8500",
            },
            {
                "environment": EnvironmentType.STAGING,
                "consul_urls": ["http://localhost:8500"],
                "consul_token": None,
                "consul_cache_ttl": 300,
            },
        ),
    ],
)
def test_environment_variables(env_vars, expected):
    """Test environment variable configuration with different scenarios."""
    with patch.dict("os.environ", env_vars, clear=True):
        settings = HomelabSettings()

        assert settings.environment == expected["environment"]
        assert settings.consul_urls == expected["consul_urls"]

        if expected["consul_token"] is None:
            assert settings.consul_token is None
        else:
            assert settings.consul_token.get_secret_value() == expected["consul_token"]

        assert settings.consul_cache_ttl == expected["consul_cache_ttl"]


@pytest.mark.parametrize(
    "env_name",
    [
        "dev",
        "staging",
        "prod",
    ],
)
def test_environment_type_validation(env_name):
    """Test environment type validation."""
    settings = HomelabSettings(
        environment=env_name,
        consul_urls="http://localhost:8500",
    )
    assert settings.environment == env_name


def test_invalid_environment_type():
    """Test invalid environment type."""
    with pytest.raises(ValidationError) as exc_info:
        HomelabSettings(
            environment="invalid",
            consul_urls="http://localhost:8500",
        )
    assert "Input should be 'dev', 'staging' or 'prod'" in str(exc_info.value)


@pytest.mark.parametrize(
    "env_name,env_value",
    [
        ("HOMELAB_ENVIRONMENT", "dev"),
        ("homelab_environment", "dev"),
        ("HomeLab_Environment", "dev"),
    ],
)
def test_case_insensitive_env_vars(env_name, env_value):
    """Test case-insensitive environment variable handling.

    Tests multiple case variations of environment variable names to ensure
    they are all handled correctly regardless of case.
    """
    env_vars = {
        env_name: env_value,
        "HOMELAB_CONSUL_URLS": "http://localhost:8500",
    }

    with patch.dict("os.environ", env_vars, clear=True):
        settings = HomelabSettings()
        assert settings.environment == EnvironmentType.DEV
        assert settings.consul_urls == ["http://localhost:8500"]


@pytest.mark.parametrize(
    "env_vars,expected_env",
    [
        ({"HOMELAB_ENVIRONMENT": "dev"}, EnvironmentType.DEV),
        ({"HOMELAB_ENVIRONMENT": "staging"}, EnvironmentType.STAGING),
        ({"HOMELAB_ENVIRONMENT": "prod"}, EnvironmentType.PROD),
    ],
)
def test_environment_value_parsing(env_vars, expected_env):
    """Test environment value parsing with different valid values."""
    env_vars["HOMELAB_CONSUL_URLS"] = "http://localhost:8500"

    with patch.dict("os.environ", env_vars, clear=True):
        settings = HomelabSettings()
        assert settings.environment == expected_env
