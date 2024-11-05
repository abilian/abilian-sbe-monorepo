# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import field, frozen

if TYPE_CHECKING:
    from abilian.services import Service


@frozen
class ServiceManager:
    """Provides lifecycle (register/start/stop) support for services."""

    services: dict[str, Service] = field(factory=dict)

    def add_service(self, name: str, service: Service):
        self.services[name] = service

    def get_service(self, name: str) -> Service:
        return self.services[name]

    def start_services(self, services: list[str] | None = None):
        """Start all services. If a service is already running, nothing happens."""
        if services is None:
            services = self.services.values()
        for service in services:
            if not service.running:
                service.start()

    def stop_services(self):
        """Stop all services. If a service is not running, nothing happens."""
        for service in self.services.values():
            if service.running:
                service.stop()

    def list_services(self):
        return self.services.values()
