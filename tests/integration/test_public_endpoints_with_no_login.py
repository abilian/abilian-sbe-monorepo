from __future__ import annotations

import warnings

from flask.testing import FlaskClient

from abilian.app import Application
from abilian.services import security_service
from abilian.web import url_for

from .conftest import ENDPOINTS_TO_IGNORE, PUBLIC_ENDPOINTS


def test_public_endpoints_with_no_login(client: FlaskClient, app: Application):
    warnings.simplefilter("ignore")
    security_service.start(ignore_state=True)

    errors = []
    for endpoint in PUBLIC_ENDPOINTS:
        if endpoint in ENDPOINTS_TO_IGNORE:
            continue
        try:
            url = url_for(endpoint)
            response = client.get(url)
            assert response.status_code in {200, 302}
        except Exception as e:
            errors.append(f"Failed: {endpoint} :\n{e}\n")

    security_service.stop()
    if errors:
        print(errors)
        raise AssertionError("Some public web tests failed")
