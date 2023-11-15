"""
"""

import warnings
from collections.abc import Iterator

from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import Rule

from abilian.app import Application
from abilian.core.models.subjects import User
from abilian.services import get_service, security_service
from abilian.services.security import Admin
from abilian.web import url_for

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

ENDPOINTS_TO_IGNORE = [
    "login.logout",
    "notifications.debug_social",
]


def all_rules_to_test(app: Application) -> Iterator[Rule]:
    rules = []
    for rule in app.url_map.iter_rules():
        if "GET" not in rule.methods:
            continue

        if rule.arguments:
            continue

        rules.append(rule)
    return sorted(rules, key=lambda r: r.endpoint)


def test_public_endpoints_with_no_login(client, app: Application):
    warnings.simplefilter("ignore")
    security_service.start(ignore_state=True)

    errors = []
    for endpoint in PUBLIC_ENDPOINTS:
        if endpoint in ENDPOINTS_TO_IGNORE:
            continue
        try:
            url = url_for(endpoint)
            r = client.get(url)
            assert r.status_code in [200, 302]
        except Exception as e:
            errors.append(f"Failed: {endpoint} :\n{e}\n")

    security_service.stop()
    if errors:
        print(errors)
        raise AssertionError("Some public web tests failed")


def test_all_simple_endpoints_with_no_login(client, app: Application):
    warnings.simplefilter("ignore")
    security_service.start(ignore_state=True)

    for rule in all_rules_to_test(app):
        if rule.endpoint in ENDPOINTS_TO_IGNORE:
            continue

        url = url_for(rule.endpoint)
        try:
            r = client.get(url)
            assert r.status_code in [200, 302, 403]
        except Exception as e:
            print("Failed:", rule.endpoint, ":", str(e))
            raise


def test_all_simple_endpoints_as_admin(client, app: Application, db: SQLAlchemy):
    # FIXME: not done yet
    warnings.simplefilter("ignore")
    # app.services['security'].start()

    login_as_admin(client, db)

    errors = []
    for rule in all_rules_to_test(app):
        endpoint = rule.endpoint

        if endpoint in ENDPOINTS_TO_IGNORE:
            continue

        if endpoint.endswith(".list_json2") or endpoint.endswith(".export_xls"):
            continue

        url = url_for(endpoint)

        try:
            r = client.get(url)
        except BaseException:
            errors.append((endpoint, "500", rule.rule))
            continue

        errors.append((endpoint, str(r.status_code), rule.rule))
        if r.status_code != 200:
            print(endpoint, r.status_code, rule.rule)
    # assert r.status_code == 200, "for endpoint = '{}'".format(rule.endpoint)

    print(78 * "-")
    for t in errors:
        print(" ".join(t))
    print()


def test_login_as_admin(client, db: SQLAlchemy):
    login_as_admin(client, db)


def test_failed_login(client, db: SQLAlchemy):
    data = {"email": "test@example.com", "password": "admin"}
    r = client.post(url_for("login.login_post"), data=data)
    assert r.status_code == 401


#
# Util
#
def login_as_admin(client, db: SQLAlchemy):
    email = "admin@example.com"
    password = "secret"  # noqa: S105
    user = User(email=email, can_login=True, password=password)

    # Needed for grant_role to not raise an exception
    db.session.add(user)

    security = get_service("security")
    security.grant_role(user, Admin)

    db.session.add(user)
    db.session.flush()

    data = {"email": email, "password": password}
    r = client.post(url_for("login.login_post"), data=data)
    assert r.status_code == 302


def logout(client):
    raise NotImplementedError()
