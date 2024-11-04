from __future__ import annotations

import importlib
from warnings import warn

from attrs import frozen
from flask import Flask

CORE_PLUGINS = [
    "abilian.web.search",
    "abilian.web.tags",
    "abilian.web.comments",
    "abilian.web.uploads",
    "abilian.web.attachments",
]


@frozen
class PluginManager:
    """Mixin that provides support for loading plugins."""

    app: Flask

    def register_plugin(self, name: str):
        """Load and register a plugin given its package name."""
        module = importlib.import_module(name)
        module.register_plugin(self.app)  # type: ignore

    def register_plugins(self, plugins: list[str]):
        """Load plugins listed in config variable 'PLUGINS'."""
        registered = set()
        for plugin_fqdn in plugins:
            if plugin_fqdn not in registered:
                try:
                    self.register_plugin(plugin_fqdn)
                except ValueError as e:
                    # FIXME: shouldn't happen
                    print(f"Failed to register plugin {plugin_fqdn}: {e}")
                    warn(f"Failed to register plugin {plugin_fqdn}: {e}")
                except Exception as e:
                    raise
                registered.add(plugin_fqdn)
