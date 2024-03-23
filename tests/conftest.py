"""Configuration and injectable fixtures for Pytest.
"""

from collections.abc import Iterator
from typing import Any

from flask import Flask
from flask.ctx import AppContext
from pytest import fixture

from abilian.core.sqlalchemy import SQLAlchemy
from abilian.sbe.app import create_app


class TestConfig:
    TESTING = True
    DEBUG = True
    SECRET_KEY = "SECRET"  # noqa: S105
    SERVER_NAME = "localhost.localdomain"
    MAIL_SENDER = "tester@example.com"
    SITE_NAME = "Abilian Test"
    # WTF_CSRF_ENABLED = True
    WTF_CSRF_ENABLED = False
    BABEL_ACCEPT_LANGUAGES = ["en", "fr"]
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@fixture(scope="module")
def config() -> Any:
    return TestConfig


@fixture(scope="module")
def app(config: Any) -> Flask:
    # We currently return a fresh app for each test.
    # Using session-scoped app doesn't currently work.
    # Note: the impact on speed is minimal.
    # from abilian.sbe.app import create_app

    return create_app(config=config)


@fixture()
def db(app_context: AppContext) -> Iterator[SQLAlchemy]:
    """Return a fresh db for each test."""
    from abilian.core.extensions import db as _db
    from tests.util import cleanup_db, ensure_services_started, stop_all_services

    stop_all_services(app_context.app)
    ensure_services_started(["blob_store", "session_blob_store"])

    cleanup_db(_db)
    _db.create_all()
    yield _db

    _db.session.remove()
    cleanup_db(_db)
    stop_all_services(app_context.app)
