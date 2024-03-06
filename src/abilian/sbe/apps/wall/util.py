"""Some functions to retrieve activity entries."""

# TODO: move to the activity service ?

from __future__ import annotations

from typing import Any, cast

import sqlalchemy as sa
from flask import g
from flask_login import current_user
from werkzeug.exceptions import Forbidden

from abilian.core.extensions import db
from abilian.core.models.subjects import User
from abilian.sbe.apps.communities.models import Membership
from abilian.sbe.apps.communities.presenters import CommunityPresenter
from abilian.sbe.apps.documents.models import Document, Folder
from abilian.services import get_service
from abilian.services.activity import ActivityEntry
from abilian.services.security import READ, Admin, SecurityService


def get_recent_entries(
    num: int = 20,
    user: User | None = None,
    community: CommunityPresenter | None = None,
) -> list[Any]:
    # Check just in case
    if not current_user.has_role(Admin):
        if community and not community.has_member(current_user):
            raise Forbidden

    query = ActivityEntry.query.options(sa.orm.joinedload(ActivityEntry.object))

    if community:
        query = query.filter(
            sa.or_(
                ActivityEntry.target == g.community,
                ActivityEntry.object == g.community,
            )
        )
    if user:
        query = query.filter(ActivityEntry.actor == user)

    # Security check
    #
    # we use communities ids instead of object because as of sqlalchemy 0.8 the
    # 'in_' operator cannot be used with relationships, only foreign keys values
    if not community and not current_user.has_role(Admin):
        community_ids = Membership.query.filter(
            Membership.user_id == current_user.id
        ).values(Membership.community_id)

        # convert generator to list: we'll need it twice during query filtering
        community_ids = list(community_ids)
        if not community_ids:
            return []

        query = query.filter(
            sa.or_(
                ActivityEntry.target_id.in_(community_ids),
                ActivityEntry.object_id.in_(community_ids),
            )
        )

    query = query.order_by(ActivityEntry.happened_at.desc()).limit(1000)
    # get twice entries as needed, but ceil to 100
    limit = min(num * 2, 100)
    entries: list[ActivityEntry] = []
    deleted = False
    security = cast(SecurityService, get_service("security"))
    has_permission = security.has_permission

    for entry in query.yield_per(limit):
        if len(entries) >= num:
            break

        # Remove entries corresponding to deleted objects
        if entry.object is None:
            db.session.delete(entry)
            deleted = True
            continue

        if isinstance(entry.object, (Folder, Document)) and not has_permission(
            current_user, READ, obj=entry.object, inherit=True
        ):
            continue

        entries.append(entry)

    if deleted:
        db.session.commit()

    return entries
