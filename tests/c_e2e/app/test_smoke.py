# Copyright (c) 2012-2024, Abilian SAS

"""Smoke tests for the main pages.

The rest of the suite exercises models, services and views in isolation, so it
stays green even when the rendered page is unusable. These tests render the
pages a user actually visits and check that the layout came out whole, which is
the safety net the Bootstrap -> Tailwind migration needs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flask import url_for

from abilian.services import security_service
from tests.util import client_login

if TYPE_CHECKING:
    from flask.testing import FlaskClient

    from abilian.app import Application
    from abilian.sbe.apps.communities.models import Community

#: Pages scoped to a community, keyed by endpoint.
COMMUNITY_PAGES = [
    "wall.index",
    "documents.index",
    "forum.index",
    "wiki.index",
]

#: Pages that don't need a community.
GLOBAL_PAGES = [
    "communities.index",
    "social.home",
    "preferences.index",
]


def assert_page_is_whole(response) -> None:
    """A 200 is not enough: check the layout actually rendered."""
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "<title>" in html, "no <title>: base template did not render"
    assert "</body>" in html, "truncated page: rendering blew up mid-template"
    assert 'rel="stylesheet"' in html, "no stylesheet linked: asset plumbing is broken"


@pytest.mark.parametrize("endpoint", COMMUNITY_PAGES)
def test_community_page_renders(
    endpoint: str, community1: Community, app: Application, client: FlaskClient
) -> None:
    security_service.start()

    with client_login(client, community1.test_user):
        response = client.get(
            url_for(endpoint, community_id=community1.slug), follow_redirects=True
        )

    assert_page_is_whole(response)


@pytest.mark.parametrize("endpoint", GLOBAL_PAGES)
def test_global_page_renders(
    endpoint: str, community1: Community, app: Application, client: FlaskClient
) -> None:
    security_service.start()

    with client_login(client, community1.test_user):
        response = client.get(url_for(endpoint), follow_redirects=True)

    assert_page_is_whole(response)
