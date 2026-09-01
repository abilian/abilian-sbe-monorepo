# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import operator
from typing import TYPE_CHECKING

import pytest
from flask import Flask
from markupsafe import Markup

from abilian.web.action import (
    Action,
    Glyphicon,
    ModalActionMixin,
    StaticIcon,
    actions,
)

if TYPE_CHECKING:
    from flask.ctx import AppContext

BASIC = Action("cat_1", "basic", "Basic Action", url="http://some.where", icon="ok")
CONDITIONAL = Action(
    "cat_1",
    "conditional",
    "Conditional Action",
    url="http://condition.al",
    condition=operator.itemgetter("show_all"),
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


def setup_actions(app: Flask) -> None:
    # fix singleton multiple initialization:
    if actions.installed(app):
        actions.clear()
    else:
        actions.init_app(app)
    for a in ALL_ACTIONS:
        a.enabled = True
    actions.register(*ALL_ACTIONS)
    actions._init_context(app)
    actions.context["show_all"] = True


def test_installed(app: Flask) -> None:
    assert actions.installed()  # test current_app (==self.app)
    assert actions.installed(app)
    assert not actions.installed(Flask("dummyapp"))


def test_actions(app: Flask) -> None:
    all_actions = actions.actions()
    assert "cat_1" in all_actions
    assert "cat_2:sub" in all_actions
    assert all_actions["cat_1"] == [BASIC, CONDITIONAL]
    assert all_actions["cat_2:sub"] == [OTHER_CAT]


def test_for_category(app: Flask) -> None:
    cat_1 = actions.for_category("cat_1")
    assert cat_1 == [BASIC, CONDITIONAL]

    cat_2 = actions.for_category("cat_2:sub")
    assert cat_2 == [OTHER_CAT]


def test_conditional(app: Flask, app_context: AppContext) -> None:
    actions.context["show_all"] = False
    assert actions.for_category("cat_1") == [BASIC]


def test_enabled(app: Flask) -> None:
    assert CONDITIONAL.enabled
    assert actions.for_category("cat_1") == [BASIC, CONDITIONAL]

    CONDITIONAL.enabled = False
    assert not CONDITIONAL.enabled
    assert actions.for_category("cat_1") == [BASIC]


def test_action_url_from_context() -> None:
    url = OTHER_CAT.url({"for": "having", "2 keys": "in context"})
    assert url == "http://count?2"
    assert OTHER_CAT.url({}) == "http://count?0"


def test_render(app: Flask) -> None:
    assert BASIC.render() == Markup(
        '<a class="action action-cat_1 action-cat_1-basic" '
        'href="http://some.where">'
        '<i class="fa fa-ok"></i> Basic Action</a>'
    )

    assert CONDITIONAL.render() == Markup(
        '<a class="action action-cat_1 action-cat_1-conditional '
        "inline-flex items-center px-4 py-2 text-sm font-medium rounded-md "
        'text-white bg-yellow-600 hover:bg-yellow-700" href="http://condition.al">'
        '<i class="fa fa-hand-right"></i> '
        "Conditional Action</a>"
    )

    assert OTHER_CAT.render() == Markup(
        '<a class="action action-cat_2-sub action-cat_2-sub-other '
        'custom-class" href="http://count?3">'
        '<img src="/static/icons/other.png" width="14" height="14" /> '
        "Other Action</a>"
    )


class ModalAction(ModalActionMixin, Action):
    pass


def test_modal_action_renders_a_modal_trigger(app: Flask) -> None:
    """The markup must be what initModals() actually binds.

    This once rendered `@click.prevent="$dispatch('open-modal', ...)"`, an event
    with no listener anywhere, which silently made every modal action a no-op.
    """
    action = ModalAction("cat_1", "modal", "Modal Action", url="#modal-thing")

    rendered = action.render()

    assert 'data-toggle="modal"' in rendered
    assert 'href="#modal-thing"' in rendered
    assert "Modal Action" in rendered
    assert "$dispatch" not in rendered


def test_css_class_keeps_tailwind_variants(app: Flask) -> None:
    """Utility classes may contain ":" and "/"; identifiers may not.

    The sanitizer used to run over the whole class string, turning
    "hover:bg-blue-700" into a class that does not exist.
    """
    action = Action(
        "cat:with:colons", "name", "T", url="/", css="hover:bg-blue-700 bg-black/50"
    )

    assert "hover:bg-blue-700" in action.css_class
    assert "bg-black/50" in action.css_class
    assert "cat-with-colons" in action.css_class
