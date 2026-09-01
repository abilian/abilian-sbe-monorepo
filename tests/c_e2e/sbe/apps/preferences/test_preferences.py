# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from flask import Flask, url_for


def test_sbe_notifications(app: Flask, client, login_user) -> None:
    response = client.get(url_for("preferences.sbe_notifications"))
    assert response.status_code == 200
