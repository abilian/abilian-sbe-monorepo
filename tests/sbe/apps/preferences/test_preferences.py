from __future__ import annotations

import pytest
from flask import Flask, url_for


@pytest.mark.skip("FIXME ASAP")
def test_sbe_notifications(app: Flask, client, login_user):
    response = client.get(url_for("preferences.sbe_notifications"))
    assert response.status_code == 200
