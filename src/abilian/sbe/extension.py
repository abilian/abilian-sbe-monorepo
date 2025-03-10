# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import uuid
from importlib import resources as rso
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from abilian.core.util import fqcn
from abilian.extensions import asset_manager

if TYPE_CHECKING:
    from collections.abc import Callable

    from abilian.app import Application


STATIC_DIR = str(rso.files("abilian.sbe") / "static")
LESSCSS_FILE = str(Path(STATIC_DIR, "less", "abilian-sbe.less"))
JS = (
    "js/sbe-datatable.js",
    "js/folder.js",
    "js/folder_edit.js",
    "js/folder_gallery.js",
    "js/folder_upload.js",
    "js/document_viewer.js",
    "vendor/bootstrap-tagsinput.js",
    "vendor/jquery.fileapi.js",
)


class AbilianSBE:
    """Base extension required by abilian.sbe.apps."""

    def __init__(self, app: Application | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Application) -> None:
        # False: it's ok if antivirus task was run but service couldn't get a
        # result
        app.config.setdefault("ANTIVIRUS_CHECK_REQUIRED", False)
        app.config.setdefault("SBE_FORUM_REPLY_BY_MAIL", False)

        if FQCN in app.extensions:
            return

        app.extensions[FQCN] = self

        # register i18n
        app.extensions["babel"].add_translations("abilian.sbe")

        # sbe static assets
        app.add_static_url("abilian/sbe", STATIC_DIR, endpoint="abilian_sbe_static")
        app.extensions["webassets"].append_path(
            STATIC_DIR, f"{app.static_url_path}/abilian/sbe"
        )

        asset_manager.register_asset("js", *JS)
        asset_manager.register_asset("css", LESSCSS_FILE)

        # Jinja
        logger.info("Register jinja context processors")
        app.context_processor(inject_template_utils)


FQCN = fqcn(AbilianSBE)
sbe = AbilianSBE()


def inject_template_utils() -> dict[str, Callable]:
    return {"uuid": uuid.uuid1}
