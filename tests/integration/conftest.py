"""Configuration specific to integratin tests.

Note: app is extranet.app
"""

import shutil
from pathlib import Path

from pytest import fixture

from extranet.app import create_app
from ..conftest import TestConfig


@fixture(scope="session")
def instance_path(tmpdir_factory):
    instance_path = str(tmpdir_factory.mktemp("instance"))
    tmp_dir = Path(instance_path)
    (tmp_dir / "tmp").mkdir()
    (tmp_dir / "cache").mkdir()
    (tmp_dir / "data").mkdir()

    yield instance_path

    shutil.rmtree(str(instance_path))


@fixture(scope="module")
def app(instance_path):
    return create_app(TestConfig())
