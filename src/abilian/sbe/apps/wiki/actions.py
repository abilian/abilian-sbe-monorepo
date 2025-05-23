# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from flask import Flask, url_for
from flask_babel import lazy_gettext as _l
from flask_login import current_user

from abilian.sbe.apps.communities.actions import CommunityEndpoint
from abilian.sbe.apps.communities.security import is_manager
from abilian.services import get_service
from abilian.services.security import ADMIN, SecurityService
from abilian.web.action import Action, FAIcon, ModalActionMixin, actions

if TYPE_CHECKING:
    from flask.blueprints import BlueprintSetupState


class WikiPageAction(Action):
    Endpoint = CommunityEndpoint

    def pre_condition(self, context: dict[str, Any]) -> bool:
        page = context.get("object")
        return bool(page)

    def url(self, context=None):
        if self._url:
            return self._url
        page = context.get("object")
        kw = self.endpoint.get_kwargs()
        kw["title"] = page.title
        return url_for(self.endpoint.name, **kw)


def is_admin(context):
    security = cast("SecurityService", get_service("security"))
    return security.has_role(current_user, ADMIN, object=context.get("object"))


class WikiPageModalAction(ModalActionMixin, WikiPageAction):
    pass


class WikiAction(Action):
    Endpoint = CommunityEndpoint


_actions = (
    WikiPageAction(
        "wiki:page",
        "page_viewers",
        _l("Readers list"),
        icon="user",
        condition=lambda ctx: is_manager(context=ctx),
        endpoint=".page_viewers",
    ),
    WikiPageAction(
        "wiki:page",
        "view",
        _l("View"),
        endpoint=".page",
        icon="eye-open",
    ),
    WikiPageAction(
        "wiki:page",
        "edit",
        _l("Edit"),
        endpoint=".page_edit",
        icon="pencil",
    ),
    WikiPageModalAction(
        "wiki:page",
        "upload_attachment",
        _l("Upload an attachment"),
        url="#upload-files",
        icon="plus",
    ),
    WikiPageAction(
        "wiki:page",
        "source",
        _l("Source"),
        endpoint=".page_source",
        icon=FAIcon("code"),
    ),
    WikiPageAction(
        "wiki:page",
        "changes",
        _l("Changes"),
        endpoint=".page_changes",
        icon="time",
    ),
    WikiPageModalAction(
        "wiki:page",
        "delete",
        _l("Delete"),
        url="#modal-delete",
        icon="trash",
    ),
    WikiAction(
        "wiki:global",
        "new",
        _l("New page"),
        endpoint=".page_new",
        icon="plus",
    ),
    WikiAction(
        "wiki:global",
        "pages",
        _l("All pages"),
        endpoint=".wiki_pages",
        icon="list",
    ),
    WikiAction(
        "wiki:global",
        "help",
        _l("Syntax help"),
        endpoint=".wiki_help",
        icon="info-sign",
    ),
)


def register_actions(state: BlueprintSetupState) -> None:
    if not actions.installed(state.app):
        return

    app = cast("Flask", state.app)
    with app.app_context():
        actions.register(*_actions)
