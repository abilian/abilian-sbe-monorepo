"""Configuration and injectable fixtures for Pytest.

Reuses fixtures defined in abilian-core.
"""
import icecream
from pytest import fixture

from abilian.sbe.app import create_app
from abilian.testing.fixtures import TestConfig

pytest_plugins = [
    "abilian.testing.fixtures",
    "abilian.sbe.apps.communities.tests.fixtures",
]


icecream.install()

class NoCsrfTestConfig(TestConfig):
    WTF_CSRF_ENABLED = False


@fixture
def config():
    return NoCsrfTestConfig


@fixture
def app(config):
    """Return an App configured with config=TestConfig."""
    return create_app(config=config)


@fixture
def req_ctx(app, request_ctx):
    """Simple alias (TBR)"""
    return request_ctx
