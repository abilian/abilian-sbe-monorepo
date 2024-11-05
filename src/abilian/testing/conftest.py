# Copyright (c) 2012-2024, Abilian SAS

"""Configuration and injectable fixtures for Pytest.

Reuses fixtures defined in abilian-core.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pytest import fixture

from abilian.core.models.subjects import User
from abilian.sbe.app import create_app
from abilian.sbe.apps.communities.models import READER, Community

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask import Flask
    from flask.ctx import AppContext, RequestContext
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session

    from abilian.core.sqlalchemy import SQLAlchemy


class TestConfig:
    TESTING = True
    DEBUG = True
    SECRET_KEY = "SECRET"  # noqa: S105
    SERVER_NAME = "localhost.localdomain"
    MAIL_SENDER = "tester@example.com"
    SITE_NAME = "Abilian Test"
    PREFERRED_URL_SCHEME = "http"
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


@fixture
def db(app: Flask, app_context: AppContext) -> Iterator[SQLAlchemy]:
    """Return a fresh db for each test."""
    from abilian.core.extensions import db as _db

    from .util import cleanup_db, ensure_services_started, stop_all_services

    stop_all_services(app)
    ensure_services_started(["blob_store", "session_blob_store"])

    cleanup_db(_db)
    _db.create_all()
    yield _db

    _db.session.remove()
    cleanup_db(_db)
    stop_all_services(app)


@fixture
def app_context(app: Flask) -> Iterator[AppContext]:
    with app.app_context() as ctx:
        yield ctx


@fixture
def test_request_context(app: Flask) -> Iterator[RequestContext]:
    with app.test_request_context() as ctx:
        yield ctx


@fixture
def session(db: SQLAlchemy) -> Session:
    return db.session


@fixture
def db_session(db: SQLAlchemy) -> Session:
    return db.session


@fixture
def user(db: SQLAlchemy) -> User:
    from abilian.core.models.subjects import User

    user = User(
        first_name="Joe",
        last_name="Test",
        email="test@example.com",
        password="test",  # noqa: S106
        can_login=True,
    )
    db.session.add(user)
    db.session.flush()
    return user


@fixture
def admin_user(db: SQLAlchemy) -> User:
    from abilian.core.models.subjects import User

    user = User(
        first_name="Jim",
        last_name="Admin",
        email="admin@example.com",
        password="admin",  # noqa: S106
        can_login=True,
    )
    user.is_admin = True
    db.session.add(user)
    db.session.flush()
    return user


@fixture
def login_user(user: User, client: FlaskClient) -> User:
    with client.session_transaction() as session:
        session["_user_id"] = user.id

    return user


@fixture
def login_admin(admin_user: User, client: FlaskClient) -> User:
    with client.session_transaction() as session:
        session["_user_id"] = admin_user.id

    return admin_user


@fixture
def community(db):
    community = Community(name="My Community")
    db.session.add(community)
    db.session.flush()
    return community


@fixture
def community1(db: SQLAlchemy) -> Community:
    community = Community(name="My Community")
    db.session.add(community)

    user = User(
        email="user_1@example.com",
        password="azerty",  # noqa: S106
        can_login=True,
    )
    db.session.add(user)
    community.set_membership(user, READER)
    community.test_user = user

    db.session.flush()
    return community


@fixture
def community2(db: SQLAlchemy) -> Community:
    community = Community(name="Another Community")
    db.session.add(community)

    user = User(
        email="user_2@example.com",
        password="azerty",  # noqa: S106
        can_login=True,
    )
    db.session.add(user)
    community.set_membership(user, READER)
    community.test_user = user

    db.session.flush()
    return community
