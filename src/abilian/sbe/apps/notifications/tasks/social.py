# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import html2text
from flask import current_app
from flask_mail import Message
from loguru import logger
from sqlalchemy import and_, or_
from validate_email import validate_email

from abilian.core.dramatiq.scheduler import crontab
from abilian.core.dramatiq.singleton import dramatiq
from abilian.core.models.subjects import User
from abilian.core.util import md5
from abilian.i18n import render_template_i18n
from abilian.sbe.apps.documents.models import Document
from abilian.sbe.apps.documents.repository import content_repository
from abilian.sbe.apps.forum.models import Post, Thread
from abilian.sbe.apps.notifications import TOKEN_SERIALIZER_NAME
from abilian.sbe.apps.wiki.models import WikiPage
from abilian.services import get_service
from abilian.services.activity import ActivityEntry
from abilian.services.auth.views import get_serializer
from abilian.web import url_for

if TYPE_CHECKING:
    from abilian.core.entities import Entity
    from abilian.sbe.apps.communities.models import Community


@crontab("SCHEDULE_SEND_DAILY_SOCIAL_DIGEST")
@dramatiq.actor()
def send_daily_social_digest_task() -> None:
    logger.debug("Running job: send_daily_social_digest_task")
    with current_app.test_request_context("/tasks/send_daily_social_updates"):
        config = current_app.config
        if not config.get("PRODUCTION") or config.get("DEMO"):
            return

        send_daily_social_digest()


def send_daily_social_digest() -> None:
    for user in User.query.filter(User.can_login == True).all():
        preferences = get_service("preferences")
        prefs = preferences.get_preferences(user)

        if not prefs.get("sbe:notifications:daily", False):
            continue

        # Defensive programming.
        if not validate_email(user.email):
            continue

        try:
            send_daily_social_digest_to(user)
        except BaseException:
            logger.opt(exception=True).exception("Error sending daily social digest")


def send_daily_social_digest_to(user: User) -> int:
    """Send to a given user a daily digest of activities in its communities.

    Return 1 if mail sent, 0 otherwise.
    """
    mail = current_app.extensions["mail"]

    message = make_message(user)
    if message:
        mail.send(message)
        return 1
    return 0


def make_message(user: User) -> Message | None:
    config = current_app.config
    sender = config.get("BULK_MAIL_SENDER", config["MAIL_SENDER"])
    sbe_config = config["ABILIAN_SBE"]
    subject = sbe_config["DAILY_SOCIAL_DIGEST_SUBJECT"]

    recipient = user.email
    digests = []
    happened_after = datetime.utcnow() - timedelta(days=1)
    list_id = '"{} daily digest" <daily.digest.{}>'.format(
        config["SITE_NAME"], config.get("SERVER_NAME", "example.com")
    )
    base_extra_headers = {
        "List-Id": list_id,
        "List-Post": "NO",
        "Auto-Submitted": "auto-generated",
        "X-Auto-Response-Suppress": "All",
        "Precedence": "bulk",
    }

    for membership in user.communautes_membership:
        community = membership.community
        if not community:
            # TODO: should not happen but it does. Fix root cause instead.
            continue
        # create an empty digest
        digest = CommunityDigest(community)
        AE = ActivityEntry
        activities = (
            AE.query.order_by(AE.happened_at.asc())
            .filter(
                and_(
                    AE.happened_at > happened_after,
                    or_(
                        and_(
                            AE.target_type == community.object_type,
                            AE.target_id == community.id,
                        ),
                        and_(
                            AE.object_type == community.object_type,
                            AE.object_id == community.id,
                        ),
                    ),
                )
            )
            .all()
        )

        # fill the internal digest lists with infos
        # seen_entities, new_members, new_documents, updated_documents ...
        for activity in activities:
            digest.update_from_activity(activity, user)
        # if activities:
        #   import ipdb; ipdb.set_trace()
        # save the current digest in the master digests list
        if not digest.is_empty():
            digests.append(digest)

    if not digests:
        return None

    token = generate_unsubscribe_token(user)
    unsubscribe_url = url_for(
        "notifications.unsubscribe_sbe",
        token=token,
        _external=True,
        _scheme=config["PREFERRED_URL_SCHEME"],
    )
    extra_headers = dict(base_extra_headers)
    extra_headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"

    msg = Message(
        subject, sender=sender, recipients=[recipient], extra_headers=extra_headers
    )
    ctx = {"digests": digests, "token": token, "unsubscribe_url": unsubscribe_url}
    msg.html = render_template_i18n("notifications/daily-social-digest.html", **ctx)
    msg.body = html2text.html2text(msg.html)
    return msg


def generate_unsubscribe_token(user: User) -> str:
    """Generates a unique unsubscription token for the specified user.

    :param user: The user to work with
    """
    data = [str(user.id), md5(user.password)]
    return get_serializer(TOKEN_SERIALIZER_NAME).dumps(data)


class CommunityDigest:
    def __init__(self, community: Community) -> None:
        self.community = community

        self.seen_entities: set[Entity] = set()
        self.new_members: list[User] = []
        self.new_documents: list[Document] = []
        self.updated_documents: list[Document] = []
        self.new_conversations: list[Post] = []
        self.updated_conversations: dict[Post, dict] = {}
        self.new_wiki_pages: list[WikiPage] = []
        self.updated_wiki_pages: dict[WikiPage, dict] = {}

    def is_empty(self) -> bool:
        return (
            not self.new_members
            and not self.new_documents
            and not self.updated_documents
            and not self.new_conversations
            and not self.updated_conversations
            and not self.new_wiki_pages
            and not self.updated_wiki_pages
        )

    def update_from_activity(self, activity, user) -> None:
        actor = activity.actor
        obj = activity.object

        # TODO ?
        # target = activity.target

        if activity.verb == "join":
            self._update_for_join(actor)

        elif activity.verb == "post":
            self._update_for_post(actor, obj, user)

        elif activity.verb == "update":
            self._update_for_update(actor, obj, user)

    def _update_for_join(self, actor) -> None:
        self.new_members.append(actor)

    def _update_for_post(self, actor, obj, user) -> None:
        if obj is None:
            return
        if obj.id in self.seen_entities:
            return

        self.seen_entities.add(obj.id)

        if isinstance(obj, Document) and content_repository.has_access(user, obj):
            self.new_documents.append(obj)
        elif isinstance(obj, WikiPage):
            self.new_wiki_pages.append(obj)
        elif isinstance(obj, Thread):
            self.new_conversations.append(obj)
        elif isinstance(obj, Post):
            if obj.thread.id not in self.seen_entities:
                # save actor and oldest/first modified Post in thread
                # oldest post because Activities are ordered_by
                # Asc(A.happened_at)
                self.updated_conversations[obj.thread] = {
                    "actors": [actor],
                    "post": obj,
                }
                # Mark this post's Thread as seen to avoid duplicates
                self.seen_entities.add(obj.thread.id)
            elif obj.thread not in self.new_conversations:
                # this post's Thread has already been seen in another Activity
                # exclude it to avoid duplicates but save the Post's actor
                self.updated_conversations[obj.thread]["actors"].append(actor)

    def _update_for_update(self, actor, obj, user) -> None:
        if obj is None:
            return
        # special case for Wikipage, we want to know each updater
        if isinstance(obj, WikiPage):
            if obj in self.updated_wiki_pages:
                page = self.updated_wiki_pages[obj]
                if actor in page:
                    page[actor] += 1
                else:
                    page[actor] = 1
            else:
                self.updated_wiki_pages[obj] = {actor: 1}

        # fast return for all other objects
        if obj.id in self.seen_entities:
            return
        self.seen_entities.add(obj.id)

        # all objects here need to be accounted only once
        if isinstance(obj, Document) and content_repository.has_access(user, obj):
            self.updated_documents.append(obj)
