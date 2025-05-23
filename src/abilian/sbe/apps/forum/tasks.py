# Copyright (c) 2012-2024, Abilian SAS

"""Dramatiq tasks related to document transformation and preview."""

from __future__ import annotations

import email
import mailbox
import re
from os.path import expanduser
from pathlib import Path
from typing import Any

import bleach
import chardet
import html2text
from bleach.css_sanitizer import CSSSanitizer
from flask import current_app, g
from flask_babel import get_locale
from flask_mail import Message
from itsdangerous import Serializer
from loguru import logger

from abilian.core.dramatiq.scheduler import crontab
from abilian.core.dramatiq.setup import RATE_LIMITER
from abilian.core.dramatiq.singleton import dramatiq
from abilian.core.extensions import db, mail
from abilian.core.models.subjects import User
from abilian.core.signals import activity
from abilian.core.util import md5, unwrap
from abilian.i18n import _l, render_template_i18n
from abilian.web import url_for

from .forms import ALLOWED_ATTRIBUTES, ALLOWED_STYLES, ALLOWED_TAGS
from .models import Post, PostAttachment, Thread

MAIL_REPLY_MARKER = _l("_____Write above this line to post_____")


@dramatiq.actor(max_retries=20, max_backoff=86400000)
def send_post_by_email(post_id: int | str) -> None:
    """Send a post to community members by email.

    max_retries = 20 (Dramatiq default)
    max_backoff = 86400000 , i.e. 1 day
    """
    with current_app.test_request_context("/tasks/send_post_by_email"):
        post = Post.query.get(post_id)
        if post is None:
            # deleted after task queued, but before task run
            return

        thread = post.thread
        community = thread.community
        logger.info(
            "Sending new post by email to members of community {community}",
            community=repr(community.name),
        )

        CHUNK_SIZE = 20
        members_id = [member.id for member in community.members if member.can_login]
        chunk = []
        for idx, member_id in enumerate(members_id):
            chunk.append(member_id)
            if idx % CHUNK_SIZE == 0:
                batch_send_post_to_users(post.id, chunk)
                chunk = []

        if chunk:
            batch_send_post_to_users(post.id, chunk)


# FIXME: add the dramatiq backernd for rate limit
# @shared_task(max_retries=10, rate_limit="12/m")
@dramatiq.actor(max_retries=20, max_backoff=86400000)
def batch_send_post_to_users(post_id, members_id, failed_ids=None):
    """Task run from send_post_by_email; auto-retry for mails that could not be
    successfully sent.

    Task default rate limit is 6/min.: there is at least 5 seconds between 2
    batches.

    During retry, if all `members_id` fails again, the task is retried
    5min. later, then 10, 20, 40... up to 10 times before giving up. This ensures
    retries up to approximatively 3 days and 13 hours after initial attempt
    (geometric series is: 5min * (1-2**10) / 1-2) = 5115 mins).
    """
    if not members_id:
        return None

    post = Post.query.get(post_id)
    if post is None:
        # deleted after task queued, but before task run
        return None
    with RATE_LIMITER[0].acquire():
        logger.debug(
            "post_id={post_id} members_id={members_id} failed_ids={failed_ids}",
            post_id=post_id,
            members_id=members_id,
            failed_ids=failed_ids,
        )
        failed = set()
        successfully_sent = []
        thread = post.thread
        community = thread.community
        user_filter = (
            User.id.in_(members_id) if len(members_id) > 1 else User.id == members_id[0]
        )
        users = User.query.filter(user_filter).all()

        for user in users:
            try:
                with current_app.test_request_context("/send_post_by_email"):
                    send_post_to_user(community, post, user)
            except BaseException:
                failed.add(user.id)
            else:
                successfully_sent.append(user.id)

        # if failed:
        #     if failed_ids is not None:
        #         failed_ids = set(failed_ids)
        #
        #     if failed == failed_ids:
        #         # 5 minutes * (2** retry count)
        #         countdown = 300 * 2 ** batch_send_post_to_users.request.retries
        #         batch_send_post_to_users.retry([post_id, list(failed)], countdown=countdown)
        #     else:
        #         batch_send_post_to_users.apply_async([post_id, list(failed)])

        return {
            "post_id": post_id,
            "successfully_sent": successfully_sent,
            "failed": list(failed),
        }


def build_local_part(name, uid):
    """Build local part as 'name-uid-digest', ensuring length < 64."""
    key = current_app.config["SECRET_KEY"]
    serializer = Serializer(key)
    signature = serializer.dumps(uid)
    digest = md5(signature)
    local_part = f"{name}+{uid}-{digest}"

    if len(local_part) > 64:
        if (len(local_part) - len(digest) - 1) > 64:
            # even without digest, it's too long
            msg = "Cannot build reply address: local part exceeds 64 characters"
            raise ValueError(msg)
        local_part = local_part[:64]

    return local_part


def build_reply_email_address(name: str, post: Post, member: User, domain: str) -> str:
    """Build a reply-to email address embedding the locale, thread_id and
    user.id.

    :param name: (str)    first part of an email address
    :param post: Post()   to get post.thread_id
    :param member: User() to get user.id
    :param domain: (str)  the last domain name of the email address
    :return: (Unicode)    reply address for forum in the form
       test+P-fr-3-4-SDB7T5DXNZPD5YAHHVIKVOE2PM@testcase.app.tld

       'P' for 'post' - locale - thread id - user id - signature digest
    """
    locale = get_locale()
    uid = "-".join(["P", str(locale), str(post.thread_id), str(member.id)])
    local_part = build_local_part(name, uid)
    return f"{local_part}@{domain}"


def extract_email_destination(address: str) -> tuple[str, ...]:
    """Return the values encoded in the email address.

    :param address: similar to test+IjEvMy8yLzQi.xjE04-4S0IzsdicTHKTAqcqa1fE@testcase.app.tld
    :return: List() of splitted values
    """
    m = re.search(r"<(.*)>", address)
    if m:
        address = m.group(1)
    local_part = address.rsplit("@", 1)[0]
    name, ident = local_part.rsplit("+", 1)
    uid, _digest = ident.rsplit("-", 1)
    signed_local_part = build_local_part(name, uid)

    if local_part != signed_local_part:
        msg = "Invalid signature in reply address"
        raise ValueError(msg)

    values = uid.split("-")
    header = values.pop(0)
    assert header == "P"
    return tuple(values)


def has_subtag(address: str) -> bool:
    """Return True if a subtag (delimited by '+') was found
    in the name part of the address.

    :param address: email adress
    """
    name = address.rsplit("@", 1)[0]
    return "+" in name


def send_post_to_user(community, post, member) -> None:
    """Send a post though SMTP.

    Configuring Flask-Mail
    Flask-Mail is configured through the standard Flask config API.
    These are the available options:

    MAIL_SERVER : default 'localhost'
    MAIL_PORT : default 25
    MAIL_USE_TLS : default False
    MAIL_USE_SSL : default False
    MAIL_DEBUG : default app.debug
    MAIL_USERNAME : default None
    MAIL_PASSWORD : default None
    MAIL_DEFAULT_SENDER : default None
    MAIL_MAX_EMAILS : default None
    MAIL_SUPPRESS_SEND : default app.testing
    MAIL_ASCII_ATTACHMENTS : default False
    """

    message = _mail_from_post(community, post, member)

    logger.info(
        "Sending new post by email to {recipients}",
        recipients=message.recipients,
    )
    try:
        # with mail.connect() as connection:
        with current_app.app_context():
            mail.send(message)
    except BaseException as e:
        # log to sentry if enabled
        logger.error("Send mail to user failed: {error}", error=str(e))


def _mail_from_post(community, post, member) -> Message:
    """Return a mail.Message build from a post in community forum"""
    recipient = member.email
    subject = f"[{community.name}] {post.title}"
    logger.debug(
        "subject={subject} recipient={recipient}",
        subject=subject,
        recipient=recipient,
    )

    config = current_app.config
    SENDER = config.get("BULK_MAIL_SENDER", config["MAIL_SENDER"])
    SBE_FORUM_REPLY_BY_MAIL = config.get("SBE_FORUM_REPLY_BY_MAIL", False)
    SBE_FORUM_REPLY_ADDRESS = config.get("SBE_FORUM_REPLY_ADDRESS", SENDER)
    SERVER_NAME = config.get("SERVER_NAME", "example.com")

    list_id = f'"{community.name} forum" <forum.{community.slug}.{SERVER_NAME}>'
    forum_url = url_for("forum.index", community_id=community.slug, _external=True)
    forum_archive_url = url_for(
        "forum.archives", community_id=community.slug, _external=True
    )
    extra_headers = {
        "List-Id": list_id,
        "List-Archive": f"<{forum_archive_url}>",
        "List-Post": f"<{forum_url}>",
        "X-Auto-Response-Suppress": "All",
        "Auto-Submitted": "auto-generated",
    }

    if SBE_FORUM_REPLY_BY_MAIL:
        name = SBE_FORUM_REPLY_ADDRESS.rsplit("@", 1)[0]
        domain = SBE_FORUM_REPLY_ADDRESS.rsplit("@", 1)[1]
        reply_to = build_reply_email_address(name, post, member, domain)
        sender = SBE_FORUM_REPLY_ADDRESS
    else:
        sender = SENDER
        reply_to = None

    msg = Message(
        subject,
        recipients=[recipient],
        sender=sender,
        reply_to=reply_to,
        extra_headers=extra_headers,
    )

    ctx = {
        "community": community,
        "post": post,
        "member": member,
        "MAIL_REPLY_MARKER": MAIL_REPLY_MARKER,
        "SBE_FORUM_REPLY_BY_MAIL": SBE_FORUM_REPLY_BY_MAIL,
    }
    msg.html = render_template_i18n("forum/mail/new_message.html", **ctx)
    msg.body = html2text.html2text(msg.html)
    return msg


def extract_content(payload, marker):
    """Search the payload for marker, return content up to marker."""
    index = payload.rfind(marker)
    content = payload[:index]
    return content


def validate_html(payload):
    css_sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_STYLES)
    args = {
        "tags": ALLOWED_TAGS,
        "attributes": ALLOWED_ATTRIBUTES,
        "css_sanitizer": css_sanitizer,
        "strip": True,
    }
    return bleach.clean(payload, **args).strip()


def add_paragraph(newpost):
    """Add surrounding <p>newpost</p> if necessary."""
    newpost = newpost.strip()
    if not newpost.startswith("<p>"):
        newpost = f"<p>{newpost}</p>"
    return newpost


def clean_html(newpost: str) -> str:
    """Clean leftover empty blockquotes."""

    clean = re.sub(
        r"(<blockquote.*?<p>.*?</p>.*?</blockquote>)",
        "",
        newpost,
        flags=re.MULTILINE | re.DOTALL,
    )

    # this cleans auto generated reponse text (<br>timedate <a email /a><br>)
    # we reverse the string because re.sub replaces
    #  LEFTMOST NON-OVERLAPPING OCCURRENCES, and we only want the last match
    # in the string
    clean = re.sub(
        r"(>rb<.*?>a.*?=ferh\sa<.*?>rb<)",
        "",
        clean[::-1],
        flags=re.MULTILINE | re.DOTALL,
    )
    clean = clean[::-1]

    return clean


def decode_payload(part: email.message.Message) -> str:
    """Get the payload and decode (base64 & quoted printable)."""

    payload = part.get_payload(decode=True)

    if isinstance(payload, str):
        return payload

    # Please the typechecker (and make things a bit clearer)
    assert isinstance(payload, bytes)
    payload_bytes: bytes = payload

    charset = part.get_content_charset()
    if charset is not None:
        try:
            payload_str = payload_bytes.decode(charset)
        except UnicodeDecodeError:
            payload_str = payload_bytes.decode("raw-unicode-escape")
    else:
        # What about other encodings? -> using chardet
        found = chardet.detect(payload_bytes)
        payload_str = payload_bytes.decode(found["encoding"])

    return payload_str


def process(message: email.message.Message, marker: str) -> tuple[str, list[dict]]:
    """Check the message for marker presence and return the text up to it if
    present.

    :raises LookupError otherwise.
    :return: sanitized html upto marker from message and attachements
    """
    assert isinstance(message, email.message.Message)
    content = {"plain": "", "html": ""}
    attachments: list[dict[str, Any]] = []

    # Iterate all message's parts for text/*
    for part in message.walk():
        content_type = part.get_content_type()
        content_disposition = part.get("Content-Disposition")

        if content_disposition not in [None, "inline"]:
            attachments.append(
                {
                    "filename": part.get_filename(),
                    "content_type": part.get_content_type(),
                    "data": part.get_payload(decode=True),
                }
            )

        elif content_type in ["text/plain", "text/html"]:
            subtype = part.get_content_subtype()
            payload = decode_payload(part)
            content[subtype] += payload

    if marker in content["html"]:
        newpost = extract_content(content["html"], marker[:9])
        newpost = add_paragraph(validate_html(newpost))
        newpost = clean_html(newpost)
    elif marker in content["plain"]:
        newpost = extract_content(content["plain"], marker[:9])
        newpost = add_paragraph(newpost)
    elif content["html"]:
        newpost = content["html"]
        newpost = add_paragraph(validate_html(newpost))
        newpost = clean_html(newpost)
    else:
        newpost = content["plain"]
        newpost = add_paragraph(newpost)
    # else:
    #     raise LookupError(f"No marker:{marker} in email")

    return newpost, attachments


@dramatiq.actor(max_retries=20, max_backoff=86400000)
def process_email(message: email.message.Message) -> bool:
    """Email.Message object from command line script Run message (parsed
    email).

    Processing chain extract community thread post member from reply_to
    persist post in db.
    """
    app = unwrap(current_app)
    # Extract post destination from To: field, (community/forum/thread/member)
    to_address = message["To"]

    assert isinstance(to_address, str)

    if not (has_subtag(to_address)):
        logger.info(
            "Email {to_address} has no subtag, skipping...",
            to_address=repr(to_address),
        )
        return False

    try:
        infos = extract_email_destination(to_address)
        locale = infos[0]
        thread_id = infos[1]
        user_id = infos[2]
    except BaseException:
        logger.opt(exception=True).error(
            "Recipient {to_address} cannot be converted to locale/thread_id/user.id",
            to_address=repr(to_address),
        )
        return False

    # Translate marker with locale from email address
    rq_headers = [("Accept-Language", locale)]
    with app.test_request_context("/process_email", headers=rq_headers):
        marker = str(MAIL_REPLY_MARKER)

    # Extract text and attachments from message
    try:
        newpost, attachments = process(message, marker)
    except BaseException:
        logger.opt(exception=True).error("Could not Process message")
        return False

    # Persist post
    with current_app.test_request_context("/process_email", headers=rq_headers):
        g.user = User.query.get(user_id)
        thread = Thread.query.get(thread_id)
        community = thread.community
        # FIXME: check membership, send back an informative email in case of an
        # error
        post = thread.create_post(body_html=newpost)
        obj_meta = post.meta.setdefault("abilian.sbe.forum", {})
        obj_meta["origin"] = "email"
        obj_meta["send_by_email"] = True
        activity.send(app, actor=g.user, verb="post", object=post, target=community)

        for desc in attachments:
            filename = desc["filename"]
            content_type = desc["content_type"]
            data = desc["data"]
            if isinstance(data, str):
                data = data.encode("utf8")
            attachment = PostAttachment(name=filename)
            attachment.post = post
            attachment.set_content(data, content_type=content_type)
            db.session.add(attachment)

        db.session.commit()

    # Notify all parties involved
    send_post_by_email.send(post.id)
    return True


@crontab("SCHEDULE_CHECK_MAILDIR")
@dramatiq.actor(max_retries=20, max_backoff=86400000)
def check_maildir() -> None:
    """Check the MailDir for emails to be injected in Threads.

    This task is registered only if `INCOMING_MAIL_USE_MAILDIR` is True.
    By default it is run every minute.
    """
    home = expanduser("~")
    maildirpath = Path(home) / "Maildir"
    if not maildirpath.is_dir():
        msg = f"{maildirpath} must be a directory"
        raise ValueError(msg)

    incoming_mailbox = mailbox.Maildir(str(maildirpath))
    incoming_mailbox.lock()  # Useless but recommended if old mbox is used by error

    try:
        for key, message in incoming_mailbox.items():
            processed = process_email(message)

            # delete the message if all went fine
            if processed:
                del incoming_mailbox[key]

    finally:
        incoming_mailbox.close()  # Flushes all changes to disk then unlocks
