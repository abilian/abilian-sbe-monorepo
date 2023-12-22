from __future__ import annotations

import os

from flask import Flask

from abilian.core import signals


def init_hooks(app: Flask):
    @app.before_first_request
    def register_signals():
        signals.register_js_api.send(app)

    # def install_id_generator(sender, **kwargs):
    #     g.id_generator = count(start=1)
    #
    # appcontext_pushed.connect(install_id_generator)

    if os.environ.get("FLASK_VALIDATE_HTML"):
        # Workaround circular import
        from abilian.testing.validation import validate_response

        app.after_request(validate_response)
