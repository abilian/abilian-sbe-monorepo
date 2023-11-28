"""
Abilian Core services initialization.

TODO: this should be refactored, using `svcs`.
"""
from flask import Flask

from abilian.services import (
    activity_service,
    antivirus,
    audit_service,
    blob_store,
    conversion_service,
    index_service,
    preferences_service,
    security_service,
    session_blob_store,
    vocabularies_service,
)


def init_services(app: Flask) -> None:
    """Initialize all services."""

    # Abilian Core services
    security_service.init_app(app)
    blob_store.init_app(app)
    session_blob_store.init_app(app)
    audit_service.init_app(app)
    index_service.init_app(app)
    activity_service.init_app(app)
    preferences_service.init_app(app)
    conversion_service.init_app(app)
    vocabularies_service.init_app(app)
    antivirus.init_app(app)

    from abilian.web.preferences.user import UserPreferencesPanel

    preferences_service.register_panel(UserPreferencesPanel(), app)
