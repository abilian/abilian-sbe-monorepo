"""Decorators and helpers to check access to communities."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import g
from flask_login import current_user
from werkzeug.exceptions import Forbidden
from werkzeug.wrappers import Response

from abilian.core.models.subjects import User
from abilian.sbe.apps.communities.presenters import CommunityPresenter
from abilian.services import security_service
from abilian.services.security import MANAGE


def require_admin(func: Callable) -> Callable:
    @wraps(func)
    def decorated_view(*args: Any, **kwargs: Any) -> str | Response:
        is_admin = security_service.has_role(current_user, "admin")
        if not is_admin:
            raise Forbidden()
        return func(*args, **kwargs)

    return decorated_view


def require_manage(func: Callable) -> Callable:
    @wraps(func)
    def decorated_view(*args: Any, **kwargs: Any) -> Response:
        community = g.community
        if community and community.has_permission(current_user, MANAGE):
            return func(*args, **kwargs)
        is_admin = security_service.has_role(current_user, "admin")
        if not is_admin:
            raise Forbidden()
        return func(*args, **kwargs)

    return decorated_view


def require_access(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        check_access()
        return func(*args, **kwargs)

    return decorated_view


def check_access(
    community: CommunityPresenter | None = None, user: User | None = None
) -> None:
    if not has_access(community, user):
        raise Forbidden()


def has_access(
    community: CommunityPresenter | None = None, user: User | None = None
) -> bool:
    if not user:
        user = current_user
    if user.is_anonymous:
        return False

    is_admin = security_service.has_role(user, "admin")
    if is_admin:
        return True

    if not community:
        community = getattr(g, "community", None)

    if community is not None:
        return community.get_role(user) is not None

    return False


def is_manager(context: dict[str, Any] | None = None, user: User | None = None) -> bool:
    if not user:
        user = current_user
    if user.is_anonymous:
        return False

    if context:
        community = context.get("object").community  # type: ignore
    else:
        community = g.community

    if community.has_permission(user, MANAGE) or user == community.creator:
        return True

    if security_service.has_role(user, "admin"):
        return True

    return False
