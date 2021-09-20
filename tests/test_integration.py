"""
"""

import warnings

from abilian.core.models.subjects import User
from abilian.services import get_service
from abilian.services.security import Admin
from abilian.web import url_for

# PUBLIC_ENDPOINTS = [
#     'Adhesion.adhesion_create',
#     'Adhesion.adhesion_academique',
#     'Adhesion.adhesion_entreprise',
#     'Adhesion.adhesion_collectivite',
#     'Adhesion.adhesion_referencement',
#     'Adhesion.index',
#     'Adhesion.selection',
#     'Adhesion.referencement',
#     'ami_public.ami_home',
#     'calendar.calendar_ics',
#     'calendar.index',
#     'home.public',
#     'home.legal',
#     'login.forgotten_pw_form',
#     'login.login_form',
#     'evenement_public.list_view',
#     'debug.index',
#     'calendar.events_feed',
#     'api.adherents',
#     'api.amis',
#     'api.calendar',
#     'api.manifestations',
#     'api.projets',
# ]

ENDPOINTS_TO_IGNORE = [
    "admin.audit_search_users",
    "bilan.export_xls",
    "communities.new",
    "crm_excel.task_status",
    "login.logout",
    "notifications.debug_social",
]


def all_rules_to_test(app):
    rules = []
    for rule in app.url_map.iter_rules():
        if "GET" not in rule.methods:
            continue

        if rule.arguments:
            continue

        rules.append(rule)
    return sorted(rules, key=lambda r: r.endpoint)


def test_all_simple_endpoints_with_no_login(client, app, request_ctx):
    warnings.simplefilter("ignore")
    app.services["security"].start()

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


def test_all_simple_endpoints_as_admin(client, app, db, request_ctx):
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


#
# Util
#


def login_as_admin(client, db):
    email = "admin@example.com"
    password = "secret"
    user = User(email=email, can_login=True, password=password)

    security = get_service("security")
    security.grant_role(user, Admin)

    db.session.add(user)
    db.session.flush()

    data = {"email": email, "password": password}
    r = client.post(url_for("login.login_post"), data=data)
    assert r.status_code == 302


# r = client.get(url_for("debug.index"))
# print(r.data)
# print(r.json())
#
# assert current_user.email == email


def logout(client):
    raise NotImplementedError()
