from flask import Flask
from flask_talisman import DEFAULT_CSP_POLICY, Talisman

from abilian.setup.debug import init_debug_toolbar
from abilian.setup.extensions import init_extensions


def setup(app: Flask) -> None:
    init_extensions(app)

    if app.debug and not app.testing:
        init_debug_toolbar(app)

    # CSP
    if not app.debug:
        csp = app.config.get("CONTENT_SECURITY_POLICY", DEFAULT_CSP_POLICY)
        Talisman(app, content_security_policy=csp)
