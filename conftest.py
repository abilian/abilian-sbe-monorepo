"""Configuration and injectable fixtures for Pytest.

Reuses fixtures defined in abilian-core.
"""

from collections.abc import Iterator
from typing import Any

from flask import Flask
from flask.ctx import AppContext, RequestContext
from flask.testing import FlaskClient
from pytest import fixture
from sqlalchemy.orm import Session

from abilian.core.models.subjects import User
from abilian.core.sqlalchemy import SQLAlchemy
from abilian.sbe.app import create_app
from abilian.sbe.apps.communities.models import READER, Community
from tests.conftest import TestConfig


@fixture()
def config() -> Any:
    return TestConfig


@fixture()
def app(config: Any) -> Flask:
    # We currently return a fresh app for each test.
    # Using session-scoped app doesn't currently work.
    # Note: the impact on speed is minimal.
    # from abilian.sbe.app import create_app

    return create_app(config=config)


@fixture()
def app_context(app: Flask) -> Iterator[AppContext]:
    with app.app_context() as ctx:
        yield ctx


@fixture()
def test_request_context(app: Flask) -> Iterator[RequestContext]:
    with app.test_request_context() as ctx:
        yield ctx


# @fixture
# def req_ctx(app: Flask) -> Iterator[RequestContext]:
#     with app.test_request_context() as _req_ctx:
#         yield _req_ctx


@fixture()
def session(db: SQLAlchemy) -> Session:
    return db.session


@fixture()
def db_session(db: SQLAlchemy) -> Session:
    return db.session


# @fixture
# def client(app: Flask) -> FlaskClient:
#     """Return a Web client, used for testing."""
#     return app.test_client()


@fixture()
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


@fixture()
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


@fixture()
def login_user(user: User, client: FlaskClient) -> User:
    with client.session_transaction() as session:
        session["_user_id"] = user.id

    return user


@fixture()
def login_admin(admin_user: User, client: FlaskClient) -> User:
    with client.session_transaction() as session:
        session["_user_id"] = admin_user.id

    return admin_user


@fixture()
def community(db):
    community = Community(name="My Community")
    db.session.add(community)
    db.session.flush()
    return community


@fixture()
def community1(db: SQLAlchemy) -> Community:
    community = Community(name="My Community")
    db.session.add(community)

    user = User(
        email="user_1@example.com", password="azerty", can_login=True  # noqa: S106
    )
    db.session.add(user)
    community.set_membership(user, READER)
    community.test_user = user

    db.session.flush()
    return community


@fixture()
def community2(db: SQLAlchemy) -> Community:
    community = Community(name="Another Community")
    db.session.add(community)

    user = User(
        email="user_2@example.com", password="azerty", can_login=True  # noqa: S106
    )
    db.session.add(user)
    community.set_membership(user, READER)
    community.test_user = user

    db.session.flush()
    return community
