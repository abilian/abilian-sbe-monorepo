# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING

from flask_login import AnonymousUserMixin, LoginManager

if TYPE_CHECKING:
    from abilian.core.models.subjects import Group


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        from abilian.services import get_security_service

        security = get_security_service()
        return security.has_role(self, role)

    @property
    def groups(self) -> set[Group]:
        return set()


login_manager = LoginManager()
login_manager.anonymous_user = AnonymousUser
