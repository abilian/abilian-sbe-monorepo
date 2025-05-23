# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import json
from functools import partial
from typing import TYPE_CHECKING

from flask import request, url_for

from abilian.core.models.subjects import User
from abilian.services.auth import views

if TYPE_CHECKING:
    from flask.ctx import AppContext
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session

    from abilian.app import Application


def test_get_redirect_target(app: Application, app_context: AppContext) -> None:
    get_redirect_target = views.get_redirect_target
    form_url = partial(url_for, "login.login_form")

    with app.test_request_context(form_url()):
        assert get_redirect_target() == ""
        url_root = request.url_root[:-1]

    with app.test_request_context(form_url(next="/")):
        assert get_redirect_target() == f"{url_root}/"

    # test "next" from referer
    referrer = f"{url_root}/some/path"
    with app.test_request_context(form_url(), headers=[("Referer", referrer)]):
        assert get_redirect_target() == referrer

    # don't cycle if coming from 'login.*' page, like this kind of cycle:
    # forgot password form ->  login page -> success
    # -> redirect(next = forgot password form) -> ...
    referrer = url_root + url_for("login.forgotten_pw")
    with app.test_request_context(form_url(), headers=[("Referer", referrer)]):
        assert get_redirect_target() == ""

    # test open redirect is forbidden
    with app.test_request_context(form_url(next="http://google.com/test")):
        assert get_redirect_target() == ""

    # open redirect through malicious construct and browser not checking
    # Location
    with app.test_request_context(form_url(next="/////google.com")):
        assert get_redirect_target() == f"{url_root}///google.com"


def test_login_post(session: Session, client: FlaskClient) -> None:
    kwargs = {"email": "User@domain.tld", "password": "azerty", "can_login": True}
    user = User(**kwargs)
    session.add(user)
    session.flush()

    response = client.post("/user/login", data=kwargs)
    assert response.status_code == 302

    # wrong password
    d = dict(kwargs)
    d["password"] = "wrong one"  # noqa: S105
    response = client.post("/user/login", data=d)
    assert response.status_code == 401

    # login disabled
    user.can_login = False
    session.flush()
    response = client.post("/user/login", data=kwargs)
    assert response.status_code == 401


def test_api_post(session: Session, client: FlaskClient) -> None:
    kwargs = {"email": "User@domain.tld", "password": "azerty", "can_login": True}
    user = User(**kwargs)
    session.add(user)
    session.flush()

    response = client.post(
        "/user/api/login", data=json.dumps(kwargs), content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "email": "User@domain.tld",
        "username": "user@domain.tld",
        "fullname": "Unknown",
        "next_url": "",
    }

    response = client.post("/user/api/logout")
    assert response.status_code == 200


def test_forgotten_pw(app: Application, session: Session, client: FlaskClient) -> None:
    mail = app.extensions["mail"]
    kwargs = {"email": "User@domain.tld", "password": "azerty", "can_login": True}
    user = User(**kwargs)
    session.add(user)
    session.flush()

    payload = dict(**kwargs)
    del payload["password"]

    with mail.record_messages() as outbox:
        response = client.post("/user/forgotten_pw", data=payload)
        assert response.status_code == 302
        assert len(outbox) == 1

        msg = outbox[0]
        assert msg.subject == "Password reset instruction for Abilian Test"
        assert msg.recipients == ["User@domain.tld"]
        assert msg.cc == []
