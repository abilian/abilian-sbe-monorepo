"""Static configuration for the application.

TODO: add more (runtime) flexibility in plugin discovery, selection
and activation.
"""

from __future__ import annotations

import jinja2

from abilian.app import Application as BaseApplication
from abilian.core.dramatiq.setup import init_dramatiq_engine
from abilian.services import converter

from .apps.documents.repository import content_repository
from .extension import sbe

# Used for side effects, do not remove


__all__ = ["Application", "create_app"]


class Application(BaseApplication):
    APP_PLUGINS = BaseApplication.APP_PLUGINS + [
        "abilian.sbe.apps.main",
        "abilian.sbe.apps.notifications",
        "abilian.sbe.apps.preferences",
        "abilian.sbe.apps.wiki",
        "abilian.sbe.apps.wall",
        "abilian.sbe.apps.documents",
        "abilian.sbe.apps.forum",
        # "abilian.sbe.apps.calendar",
        "abilian.sbe.apps.communities",
        "abilian.sbe.apps.social",
        "abilian.sbe.apps.preferences",
    ]

    def setup(self, config: type | None) -> None:
        super().setup(config)
        loader = jinja2.PackageLoader("abilian.sbe")
        self.register_jinja_loaders(loader)

    def init_extensions(self) -> None:
        super().init_extensions()
        sbe.init_app(self)
        content_repository.init_app(self)
        converter.init_app(self)


def create_app(config: type | None = None, **kw) -> Application:
    app = Application(**kw)
    with app.app_context():
        app.setup(config)
    init_dramatiq_engine(app)
    return app
