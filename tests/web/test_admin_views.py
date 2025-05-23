# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from flask import url_for

from abilian.web.admin.panels.sysinfo import installed_packages


def test_home(client, db_session) -> None:
    response = client.get(url_for("admin.dashboard"))
    assert response.status_code == 200


def test_list_packages() -> None:
    packages = installed_packages()
    assert isinstance(packages, list)


def test_sysinfo(client, db_session) -> None:
    response = client.get(url_for("admin.sysinfo"))
    assert response.status_code == 200


def test_login_session(client, db_session) -> None:
    response = client.get(url_for("admin.login_sessions"))
    assert response.status_code == 200


def test_audit(client, db_session) -> None:
    response = client.get(url_for("admin.audit"))
    assert response.status_code == 200


def test_settings(client, db_session) -> None:
    response = client.get(url_for("admin.settings"))
    assert response.status_code == 200
