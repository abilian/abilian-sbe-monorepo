"""Mail extension for Abilian Core."""

from __future__ import annotations

from typing import Any

import flask_mail
from flask import current_app

from abilian.core.logger_patch import patch_logger


# patch flask.ext.mail.Message.send to always set enveloppe_from default mail
# sender
# FIXME: we'ld rather subclass Message and update all imports
def _message_send(self: Any, connection: flask_mail.Connection):
    """Send a single message instance.

    If TESTING is True the message will not actually be sent.

    :param self: a Message instance.
    """
    sender = current_app.config["MAIL_SENDER"]
    if not self.extra_headers:
        self.extra_headers = {}
    self.extra_headers["Sender"] = sender
    connection.send(self, sender)


patch_logger.info(flask_mail.Message.send)
flask_mail.Message.send = _message_send

mail = flask_mail.Mail()
