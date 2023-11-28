from __future__ import annotations

import importlib
import logging
from itertools import chain

from flask.config import Config

from abilian.services import Service

logger = logging.getLogger(__name__)


class ServiceManager:
    """Mixin that provides lifecycle (register/start/stop) support for
    services."""

    # TODO: refactor to use `svcs` and remove this class

    services: dict[str, Service]

    def __init__(self):
        self.services = {}

    def start_services(self):
        for svc in self.services.values():
            svc.start()

    def stop_services(self):
        for svc in self.services.values():
            svc.stop()


class PluginManager:
    """Mixin that provides support for loading plugins."""

    # TODO: refactor to use `svcs` and maybe something else and remove this class

    config: Config

    #: Custom apps may want to always load some plugins: list them here.
    APP_PLUGINS = [
        "abilian.web.search",
        "abilian.web.tags",
        "abilian.web.comments",
        "abilian.web.uploads",
        "abilian.web.attachments",
    ]

    def register_plugin(self, name: str):
        """Load and register a plugin given its package name."""
        logger.info(f"Registering plugin: {name}")
        module = importlib.import_module(name)
        module.register_plugin(self)  # type: ignore

    def register_plugins(self):
        """Load plugins listed in config variable 'PLUGINS'."""
        registered = set()
        for plugin_fqdn in chain(self.APP_PLUGINS, self.config["PLUGINS"]):
            if plugin_fqdn not in registered:
                self.register_plugin(plugin_fqdn)
                registered.add(plugin_fqdn)
