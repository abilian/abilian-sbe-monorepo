# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from flask import url_for

from abilian.sbe.apps.communities.models import Community
from abilian.services import security_service
from abilian.services.security import ADMIN
from tests.util import client_login

if TYPE_CHECKING:
    from flask.testing import FlaskClient

    from abilian.app import Application
    from abilian.core.sqlalchemy import SQLAlchemy


def test_index(
    community1: Community, app: Application, db: SQLAlchemy, client: FlaskClient
) -> None:
    security_service.start()

    user = community1.test_user
    with client_login(client, user):
        response = client.get(url_for("communities.index"))
        assert response.status_code == 200


def test_community_home(
    community1: Community, community2: Community, app: Application, client: FlaskClient
) -> None:
    security_service.start()

    url = app.default_view.url_for(community1)

    user1 = community1.test_user

    with client_login(client, user1):
        response = client.get(url)
        assert response.status_code == 302
        expected_url = url_for(
            "wall.index", community_id=community1.slug, _external=True
        )
        assert urlparse(response.location).path == urlparse(expected_url).path
        # assert response.location == expected_url

    user2 = community2.test_user
    with client_login(client, user2):
        response = client.get(url)
        assert response.status_code == 403


def test_new(
    community1: Community, app: Application, client: FlaskClient, db: SQLAlchemy
) -> None:
    # security_service.use_cache = False
    security_service.start()

    user = community1.test_user

    with client_login(client, user):
        response = client.get(url_for("communities.new"))
        assert response.status_code == 403

    security_service.grant_role(user, ADMIN)
    db.session.flush()

    with client_login(client, user):
        response = client.get(url_for("communities.new"))
        assert response.status_code == 200


def test_community_settings(
    app: Application, client: FlaskClient, community1: Community
) -> None:
    security_service.start()

    url = url_for("communities.settings", community_id=community1.slug)
    user = community1.test_user

    with client_login(client, user):
        response = client.get(url)
        assert response.status_code == 403

        security_service.grant_role(user, ADMIN)
        response = client.get(url)
        assert response.status_code == 200

        data = {
            "__action": "edit",
            "name": "edited community",
            "description": "my community",
            "linked_group": "",
            "type": "participative",
        }
        response = client.post(url, data=data, follow_redirects=True)
        assert response.status_code == 200
        assert "edited community" in response.get_data(as_text=True)


def test_members(
    app: Application,
    client: FlaskClient,
    db: SQLAlchemy,
    community1: Community,
    community2: Community,
) -> None:
    security_service.start()

    user1 = community1.test_user
    user2 = community2.test_user

    with client_login(client, user1):
        url = url_for("communities.members", community_id=community1.slug)
        response = client.get(url)
        assert response.status_code == 200

        # test add user
        data = {"action": "add-user-role", "user": user2.id}
        response = client.post(url, data=data)
        assert response.status_code == 403

        security_service.grant_role(user1, ADMIN)

        data = {"action": "add-user-role", "user": user2.id, "role": "member"}
        response = client.post(url, data=data, follow_redirects=True)
        assert response.status_code == 200

        membership = next(m for m in community1.memberships if m.user == user2)
        assert membership.role == "member"

        data["action"] = "set-user-role"
        data["role"] = "manager"
        response = client.post(url, data=data, follow_redirects=True)
        assert response.status_code == 200

        db.session.expire(membership)
        assert membership.role == "manager"

        # Community.query.session is not self.db.session, but web app
        # session.
        community = Community.query.get(community1.id)
        assert user2 in community.members

        # test delete
        data = {
            "action": "delete",
            "user": user2.id,
            "membership": next(m.id for m in community1.memberships if m.user == user2),
        }
        response = client.post(url, data=data, follow_redirects=True)
        assert response.status_code == 200
        assert user2 not in community.members
