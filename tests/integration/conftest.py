"""Configuration specific to integratin tests.

Note: app is extranet.app
"""

import shutil
from pathlib import Path

from pytest import fixture

from abilian.sbe.app import create_app

from ..conftest import TestConfig

PUBLIC_ENDPOINTS = [
    "login.forgotten_pw_form",
    "login.login_form",
    # 'calendar.calendar_ics',
    # 'calendar.index',
    # 'home.public',
    # 'home.legal',
    # 'evenement_public.list_view',
    # 'debug.index',
    # 'calendar.events_feed',
    # 'api.adherents',
    # 'api.amis',
    # 'api.calendar',
    # 'api.manifestations',
    # 'api.projets',
]

ENDPOINTS_TO_IGNORE = {
    "login.logout",
    "notifications.debug_social",
    "communities.community_default_image",
    "communities.list_json2",
    "images.user_default",
    "preferences.user",
    "search.live",
    "search.search_main",
    # Fixe later
    "social.groups",
    "social.groups_json",
    "social.groups_new",
    "social.home",
    "social.users",
    "social.users_dt_json",
    "social.users_json",
    "users.json_list",
}


@fixture(scope="module")
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
    return create_app(config=TestConfig)
