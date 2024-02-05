"""Modules that provide services.

They are implemented as Flask extensions (see:
http://flask.pocoo.org/docs/extensiondev/ )
"""

from __future__ import annotations

from flask import current_app

# This one must be imported first
from .base import Service, ServiceState

# Don't remove (used to force import order)
assert Service, ServiceState

# flake8: noqa
# Import below are flagged as problematic due to the trick above.

from .activity import ActivityService
from .antivirus import service as antivirus
from .audit import audit_service
from .auth import AuthService
from .blob_store import blob_store, session_blob_store
from .conversion import conversion_service, converter
from .indexing import service as index_service
from .preferences import preferences as preferences_service
from .security import security as security_service
from .settings import SettingsService
from .vocabularies import vocabularies as vocabularies_service

auth_service = AuthService()
activity_service = ActivityService()
settings_service = SettingsService()


def get_service(service: str) -> Service:
    return current_app.services[service]


def get_security_service():
    return security_service
