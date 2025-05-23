# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import html

import sqlalchemy as sa
import sqlalchemy.orm
from flask import render_template_string, request
from sqlalchemy.sql.expression import asc, desc, func, nullslast

from abilian.core.models.subjects import Group, User
from abilian.i18n import _l
from abilian.services import get_security_service
from abilian.services.security.models import Role
from abilian.web.action import ButtonAction, FAIcon
from abilian.web.nav import BreadcrumbItem
from abilian.web.util import url_for
from abilian.web.views import base, object as views

from .forms import GroupAdminForm


class JsonGroupsList(base.JSONView):
    """JSON group list for datatable."""

    def data(self, *args, **kw) -> dict:
        security = get_security_service()
        length = int(kw.get("iDisplayLength", 0))
        start = int(kw.get("iDisplayStart", 0))
        sort_dir = kw.get("sSortDir_0", "asc")
        echo = int(kw.get("sEcho", 0))
        search = kw.get("sSearch", "").replace("%", "").strip().lower()

        end = start + length
        query = Group.query.options(sa.orm.noload("*"))
        total_count = query.count()

        if search:
            # TODO: gérer les accents
            query = query.filter(func.lower(Group.name).like(f"%{search}%"))

        count = query.count()
        columns = [func.lower(Group.name)]
        direction = asc if sort_dir == "asc" else desc
        order_by = list(map(direction, columns))

        # sqlite does not support 'NULLS FIRST|LAST' in ORDER BY clauses
        engine = query.session.get_bind(Group.__mapper__)
        if engine.name != "sqlite":
            order_by[0] = nullslast(order_by[0])

        query = query.order_by(*order_by).add_columns(Group.members_count)
        groups = query.slice(start, end).all()
        data = []

        for group, members_count in groups:
            # TODO: this should be done on the browser.
            group_url = url_for(".groups_group", group_id=group.id)
            name = html.escape(group.name or "")
            roles = [r for r in security.get_roles(group) if r.assignable]

            columns = [
                f'<a href="{group_url}">{name}</a>',
                str(members_count or 0),
                render_template_string(
                    """{%- for role in roles %}
                        <span class="badge badge-default">{{ role }}</span>
                        {%- endfor %}""",
                    roles=roles,
                ),
                "\u2713" if group.public else "",
            ]

            data.append(columns)

        return {
            "sEcho": echo,
            "iTotalRecords": total_count,
            "iTotalDisplayRecords": count,
            "aaData": data,
        }


# Group edit / create views
class GroupBase:
    Model = Group
    Form = GroupAdminForm
    pk = "group_id"
    base_template = "admin/_base.html"

    def index_url(self):
        return url_for(".groups")

    def view_url(self):
        return url_for(".groups_group", group_id=self.obj.id)


# those buttons are made to have valid edit actions, but will not be shown in
# edit forms: they must be availabe only during POST
ADD_USER_BUTTON = ButtonAction(
    "form",
    "add_user",
    condition=lambda v: request.method == "POST",
    title=_l("Add"),
    btn_class="primary",
)

REMOVE_USER_BUTTON = ButtonAction(
    "form",
    "remove_user",
    condition=lambda v: request.method == "POST",
    btn_class="danger",
    icon=FAIcon("times"),
    title="",
)


class GroupView(GroupBase, views.ObjectView):
    template = "admin/group_view.html"

    def breadcrumb(self):
        label = render_template_string("<em>{{ g }}</em>", g=self.obj.name)
        return BreadcrumbItem(label=label, url="", description=self.obj.name)

    @property
    def template_kwargs(self):
        security = get_security_service()
        kw = super().template_kwargs
        members = list(self.obj.members)
        members.sort(key=lambda u: (u.last_name, u.first_name))
        kw["members"] = members
        kw["roles"] = sorted(
            r for r in security.get_roles(self.obj, no_group_roles=True) if r.assignable
        )
        kw["ADD_USER_BUTTON"] = ADD_USER_BUTTON
        kw["REMOVE_USER_BUTTON"] = REMOVE_USER_BUTTON
        return kw


class GroupEdit(GroupBase, views.ObjectEdit):
    def breadcrumb(self):
        label = render_template_string("<em>{{ g }}</em>", g=self.obj.name)
        return BreadcrumbItem(label=label, url="", description=self.obj.name)

    def get_form_buttons(self, *args, **kwargs):
        buttons = super().get_form_buttons()
        buttons.append(ADD_USER_BUTTON)
        buttons.append(REMOVE_USER_BUTTON)
        return buttons

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        security = get_security_service()
        roles = [
            r for r in security.get_roles(self.obj, no_group_roles=True) if r.assignable
        ]
        kw["roles"] = [role.name for role in roles]
        return kw

    def after_populate_obj(self):
        security = get_security_service()
        current_roles = security.get_roles(self.obj, no_group_roles=True)
        current_roles = {r for r in current_roles if r.assignable}
        new_roles = {Role(r) for r in self.form.roles.data}

        for r in current_roles - new_roles:
            security.ungrant_role(self.obj, r)

        for r in new_roles - current_roles:
            security.grant_role(self.obj, r)

        return super().after_populate_obj()

    def add_user(self, *args, **kwargs):
        user_id = int(request.form.get("user"))
        user = User.query.options(sa.orm.joinedload(User.groups)).get(user_id)
        self.obj.members.add(user)
        sa.orm.object_session(self.obj).commit()
        return self.redirect_to_view()

    def remove_user(self, *args, **kwargs):
        user_id = int(request.form.get("user"))
        user = User.query.options(sa.orm.joinedload(User.groups)).get(user_id)
        self.obj.members.discard(user)
        sa.orm.object_session(self.obj).commit()
        return self.redirect_to_view()


class GroupCreate(GroupBase, views.ObjectCreate):
    chain_create_allowed = True
