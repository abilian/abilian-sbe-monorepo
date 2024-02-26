"""Configuration and injectable fixtures for Pytest.
"""

import typing
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

# @fixture(scope="session")
# def config() -> Any:
#     return TestConfig


# @fixture(scope="session")
# def app(config: Any) -> Flask:
#     # We currently return a fresh app for each test.
#     # Using session-scoped app doesn't currently work.
#     # Note: the impact on speed is minimal.
#     # from abilian.sbe.app import create_app

#     return create_app(config=config)
