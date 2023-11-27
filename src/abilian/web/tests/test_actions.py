from __future__ import annotations

import pytest
from flask import Flask
from flask.ctx import AppContext
from markupsafe import Markup

from abilian.app import Application
from abilian.web.action import Action, Glyphicon, StaticIcon, actions

BASIC = Action("cat_1", "basic", "Basic Action", url="http://some.where", icon="ok")
CONDITIONAL = Action(
    "cat_1",
    "conditional",
    "Conditional Action",
    url="http://condition.al",
    condition=lambda ctx: ctx["show_all"],
    icon=Glyphicon("hand-right"),
    button="warning",
)

OTHER_CAT = Action(
    "cat_2:sub",
    "other",
    "Other Action",
    url=lambda ctx: f"http://count?{len(ctx)}",
    icon=StaticIcon("icons/other.png", size=14),
    css="custom-class",
)

ALL_ACTIONS = (BASIC, CONDITIONAL, OTHER_CAT)


@pytest.fixture(autouse=True)
def ctx(app: Flask, app_context: AppContext):
    setup_actions(app)
    return app_context


def setup_actions(app: Flask):
    actions.init_app(app)
    for a in ALL_ACTIONS:
        a.enabled = True
    actions.register(*ALL_ACTIONS)
    actions._init_context(app)
    actions.context["show_all"] = True


def test_installed(app: Flask):
    assert actions.installed()  # test current_app (==self.app)
    assert actions.installed(app)
    assert not actions.installed(Flask("dummyapp"))


def test_actions(app: Flask):
    all_actions = actions.actions()
    assert "cat_1" in all_actions
    assert "cat_2:sub" in all_actions
    assert all_actions["cat_1"] == [BASIC, CONDITIONAL]
    assert all_actions["cat_2:sub"] == [OTHER_CAT]


def test_for_category(app: Flask):
    cat_1 = actions.for_category("cat_1")
    assert cat_1 == [BASIC, CONDITIONAL]

    cat_2 = actions.for_category("cat_2:sub")
    assert cat_2 == [OTHER_CAT]


def test_conditional(app: Flask, app_context: AppContext):
    actions.context["show_all"] = False
    assert actions.for_category("cat_1") == [BASIC]


def test_enabled(app: Flask):
    assert CONDITIONAL.enabled
    assert actions.for_category("cat_1") == [BASIC, CONDITIONAL]

    CONDITIONAL.enabled = False
    assert not CONDITIONAL.enabled
    assert actions.for_category("cat_1") == [BASIC]


def test_action_url_from_context():
    url = OTHER_CAT.url({"for": "having", "2 keys": "in context"})
    assert url == "http://count?2"
    assert OTHER_CAT.url({}) == "http://count?0"


def test_render(app: Flask):
    assert BASIC.render() == Markup(
        '<a class="action action-cat_1 action-cat_1-basic" '
        'href="http://some.where">'
        '<i class="glyphicon glyphicon-ok"></i> Basic Action</a>'
    )

    assert CONDITIONAL.render() == Markup(
        '<a class="action action-cat_1 action-cat_1-conditional '
        'btn btn-warning" href="http://condition.al">'
        '<i class="glyphicon glyphicon-hand-right"></i> '
        "Conditional Action</a>"
    )

    assert OTHER_CAT.render() == Markup(
        '<a class="action action-cat_2-sub action-cat_2-sub-other '
        'custom-class" href="http://count?3">'
        '<img src="/static/icons/other.png" width="14" height="14" /> '
        "Other Action</a>"
    )
