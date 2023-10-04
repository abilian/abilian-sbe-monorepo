from __future__ import annotations


class BaseConfig:
    MAIL_ASCII_ATTACHMENTS = True

    # False: it's ok if antivirus task was run but service
    # couldn't get a result
    ANTIVIRUS_CHECK_REQUIRED = True

    BABEL_ACCEPT_LANGUAGES = ("fr", "en")

    CONTENT_SECURITY_POLICY = {
        "default-src": "'self' https://stats.abilian.com/ https://sentry.io/",
        "child-src": "'self' blob:",
        "img-src": "* data:",
        "style-src": [
            "'self'",
            "https://cdn.rawgit.com/novus/",
            "https://cdnjs.cloudflare.com/",
            "'unsafe-inline'",
        ],
        "object-src": "'self'",
        "script-src": [
            "'self'",
            "https://browser.sentry-cdn.com/",
            "https://stats.abilian.com/",
            "https://cdnjs.cloudflare.com/",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ],
        "worker-src": "'self' blob:",
    }
