"""Import Test."""

import importlib
import pkgutil

import homelab_config


def test_imports():
    """Test import modules."""
    prefix = "{}.".format(homelab_config.__name__)  # noqa
    iter_packages = pkgutil.walk_packages(
        homelab_config.__path__,
        prefix,
    )
    for _, name, _ in iter_packages:
        module_name = name if name.startswith(prefix) else prefix + name
        importlib.import_module(module_name)
