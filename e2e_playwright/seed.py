# Copyright (c) 2012-2024, Abilian SAS

"""Seed the throwaway e2e instance with a community.

Run by serve.sh via `flask script`, so it executes inside the app context.

Without a community there is nothing to point the browser at for the documents
module -- the folder listing, its DataTable, and the modal stack -- which is
where the front end is most intricate and least covered.
"""

from __future__ import annotations

import os

from abilian.core.extensions import db
from abilian.core.models.subjects import User
from abilian.sbe.apps.communities.models import MANAGER, Community

COMMUNITY_NAME = "E2E Community"
ADMIN_EMAIL = os.environ.get("E2E_EMAIL", "admin@example.com")

existing = Community.query.filter(Community.name == COMMUNITY_NAME).first()
if existing is None:
    community = Community(name=COMMUNITY_NAME)
    db.session.add(community)

    admin = User.query.filter(User.email == ADMIN_EMAIL).one()
    # MANAGER, not the global ADMIN role: set_membership only accepts
    # community roles (READER, WRITER, MANAGER, MEMBER).
    community.set_membership(admin, MANAGER)

    db.session.commit()

    # A document, so the folder listing renders its DataTable: an empty folder
    # takes a different, table-less path and would not exercise folder.js.
    doc = community.folder.create_document(title="E2E Sample.txt")
    doc.set_content(b"sample content for the e2e suite", "text/plain")
    # The listing renders url_for(..., user_id=obj.owner.id) with no guard, so a
    # document without an owner 500s the whole folder. Outside a request there is
    # no current_user to default from, so set it explicitly.
    doc.owner = admin
    doc.creator = admin
    db.session.commit()

    print(f"seeded community {community.slug!r} with 1 document for {ADMIN_EMAIL}")
else:
    print(f"community {existing.slug!r} already present")
