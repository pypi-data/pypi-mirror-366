"""Pytest configuration and fixtures."""

import os
from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def clean_env() -> Generator[None, None, None]:  # noqa: D103
    original_env = dict(os.environ)

    try:
        # 删除所有 HOMELAB_ 相关的环境变量
        for key in list(os.environ.keys()):
            if key.startswith("HOMELAB_"):
                del os.environ[key]
        yield
    finally:
        # 确保在测试结束后总是恢复原始环境变量
        os.environ.clear()
        os.environ.update(original_env)


@pytest.fixture
def mock_env():  # noqa: D103
    def _set_env(env_vars: dict[str, str]) -> None:
        for key, value in env_vars.items():
            os.environ[key] = value

    return _set_env
