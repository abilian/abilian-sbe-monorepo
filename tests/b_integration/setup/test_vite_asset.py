# Copyright (c) 2012-2024, Abilian SAS

"""Tests for the Vite asset tag helper.

The production branch of this helper once emitted `/static/vite/...`, a path
nothing serves, and no test noticed because the suite runs with DEBUG=True and
only ever exercised the dev-server branch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from abilian.setup.extensions import VITE_DEV_SERVER, vite_asset

if TYPE_CHECKING:
    from abilian.app import Application


def test_dev_mode_points_at_the_vite_dev_server(app: Application) -> None:
    with app.test_request_context():
        app.config["DEBUG"] = True
        tag = vite_asset("src/styles.css")

    assert VITE_DEV_SERVER in tag
    assert "src/styles.css" in tag


def test_dev_server_address_is_configurable(app: Application) -> None:
    with app.test_request_context():
        app.config["DEBUG"] = True
        app.config["VITE_DEV_SERVER"] = "http://elsewhere:1234"
        tag = vite_asset("src/main.js")

    assert "http://elsewhere:1234/src/main.js" in tag
    del app.config["VITE_DEV_SERVER"]


def test_production_mode_uses_the_served_static_route(app: Application) -> None:
    with app.test_request_context():
        app.config["DEBUG"] = False
        css = vite_asset("src/styles.css")
        js = vite_asset("src/main.js")
        app.config["DEBUG"] = True

    # Must match where `make front` writes and what abilian_sbe_static serves.
    assert 'href="/static/abilian/sbe/vite/styles.css"' in css
    assert 'src="/static/abilian/sbe/vite/main.js"' in js


def test_css_and_js_get_the_right_tag(app: Application) -> None:
    with app.test_request_context():
        app.config["DEBUG"] = False
        assert vite_asset("src/styles.css").startswith("<link")
        assert 'rel="stylesheet"' in vite_asset("src/styles.css")
        assert vite_asset("src/main.js").startswith("<script")
        assert 'type="module"' in vite_asset("src/main.js")
        app.config["DEBUG"] = True


def test_unknown_extension_raises(app: Application) -> None:
    """A silent "" here means a missing stylesheet nobody notices."""
    with app.test_request_context(), pytest.raises(ValueError, match=r"expected \.css"):
        vite_asset("src/mystery.woff2")
