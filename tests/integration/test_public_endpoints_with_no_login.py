from __future__ import annotations
import warnings
from collections.abc import Iterator

from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import Rule
from flask.testing import FlaskClient

from abilian.app import Application
from abilian.core.models.subjects import User
from abilian.services import get_service, security_service
from abilian.services.security import Admin
from abilian.web import url_for
from .conftest import PUBLIC_ENDPOINTS, ENDPOINTS_TO_IGNORE


def test_public_endpoints_with_no_login(client: FlaskClient, app: Application):
    from icecream import ic

    ic(app)
    warnings.simplefilter("ignore")
    security_service.start(ignore_state=True)

    errors = []
    for endpoint in PUBLIC_ENDPOINTS:
        if endpoint in ENDPOINTS_TO_IGNORE:
            continue
        try:
            url = url_for(endpoint)
            ic(url)
            response = client.get(url)
            assert response.status_code in {200, 302}
        except Exception as e:
            errors.append(f"Failed: {endpoint} :\n{e}\n")

    security_service.stop()
    if errors:
        print(errors)
        raise AssertionError("Some public web tests failed")
