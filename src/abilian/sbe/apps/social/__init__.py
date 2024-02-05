"""Default ("home") page for social apps."""

from __future__ import annotations

from abilian.sbe.app import Application


def register_plugin(app: Application) -> None:
    from .views import groups, sidebars, users
    from .views.social import social

    app.register_blueprint(social)

    # TODO: better config variable choice?
    if app.config.get("SOCIAL_REST_API"):
        from .restapi import restapi

        app.register_blueprint(restapi)
