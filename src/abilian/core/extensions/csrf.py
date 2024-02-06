""""""

from __future__ import annotations

from flask import current_app, flash, request
from flask.signals import request_started
from flask_wtf.csrf import CSRFError, CSRFProtect
from markupsafe import Markup
from werkzeug.exceptions import BadRequest

from abilian.core.util import unwrap
from abilian.i18n import _l

wtf_csrf = CSRFProtect()


class AbilianCsrf:
    """CSRF error handler, that allows supporting views to gracefully report
    error instead of a plain 400 error.

    views supporting this must
    """

    #: for views that gracefully support csrf errors, this message can be
    #: displayed to user. It can be changed if you have a better one for your
    #: users.
    csrf_failed_message = _l(
        "Security informations are missing or expired. "
        "This may happen if you have opened the form for a long time. "
        "<br /><br />"
        "Please try to resubmit the form."
    )

    def init_app(self, app):
        if "csrf" not in app.extensions:
            raise RuntimeError(
                'Please install flask_wtf.csrf.CSRFProtect() as "csrf" in '
                "extensions before AbilianCsrf()"
            )

        # FIXME
        # app.extensions["csrf"].error_handler(self.csrf_error_handler)
        # Note: deprecated since flask-wtf 0.14

        # see https://flask-wtf.readthedocs.io/en/1.2.x/changes/#version-0-14
        #     https://github.com/wtforms/flask-wtf/pull/264

        wtf_csrf.init_app(app)

        app.register_error_handler(CSRFError, self.csrf_error_handler)

        app.extensions["csrf-handler"] = self
        request_started.connect(self.request_started, sender=app)
        app.before_request(self.before_request)

    def flash_csrf_failed_message(self):
        flash(Markup(self.csrf_failed_message), "error")

    def request_started(self, app):
        request.csrf_failed = False

    def csrf_error_handler(self, reason):
        request.csrf_failed = reason

    def before_request(self):
        req = unwrap(request)
        failed = req.csrf_failed

        if not failed:
            return

        rule = req.url_rule
        view = current_app.view_functions[rule.endpoint]
        if getattr(view, "csrf_support_graceful_failure", False):
            # view can handle it nicely for the user
            return

        if hasattr(view, "view_class") and getattr(
            view.view_class, "csrf_support_graceful_failure", False
        ):
            return

        raise BadRequest(failed)


abilian_csrf = AbilianCsrf()
