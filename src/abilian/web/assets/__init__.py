# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import typing
from importlib import resources as rso

from flask import current_app, url_for
from flask_assets import Bundle
from webassets.filter import get_filter

from abilian.services.security import ANONYMOUS

from .filters import register_filters

if typing.TYPE_CHECKING:
    from abilian.app import Application


def init_app(app: Application) -> None:
    register_filters()

    # Keep the static URL for legacy assets like favicons
    app.add_static_url(
        "abilian", RESOURCES_DIR, endpoint="abilian_static", roles=ANONYMOUS
    )


# RequireJS configuration removed - now using Alpine.js and modern ES modules


RESOURCES_DIR = str(rso.files("abilian.web") / "resources")

JQUERY = Bundle("jquery/js/jquery-1.11.3.js")

BOOTBOX_JS = Bundle("bootbox/bootbox.js")

# BOOTSTRAP_LESS = Bundle("bootstrap/less/bootstrap.less")  # Removed in favor of Tailwind
# BOOTSTRAP_JS = Bundle("bootstrap/js/bootstrap.js")  # Removed in favor of Alpine.js

# Tailwind CSS (built from vite directory)
TAILWIND_CSS = Bundle("../../vite/dist/styles.css")

# Alpine.js for interactive components (replaces Bootstrap JS)
ALPINE_JS = Bundle("https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js")

BOOTSTRAP_DATEPICKER_LESS = "bootstrap-datepicker/less/datepicker.less"
BOOTSTRAP_DATEPICKER_JS = Bundle("bootstrap-datepicker/js/bootstrap-datepicker.js")

BOOTSTRAP_SWITCH_LESS = Bundle("bootstrap-switch/less/bootstrap3/bootstrap-switch.less")
BOOTSTRAP_SWITCH_JS = Bundle("bootstrap-switch/bootstrap-switch.js")

BOOTSTRAP_TIMEPICKER_LESS = Bundle("bootstrap-timepicker/less/timepicker.less")
BOOTSTRAP_TIMEPICKER_JS = Bundle("bootstrap-timepicker/js/bootstrap-timepicker.js")

DATATABLE_LESS = Bundle(
    "datatables/css/jquery.dataTables.css",
    "datatables/css/jquery.dataTables_themeroller.css",
)
DATATABLE_JS = Bundle("datatables/js/jquery.dataTables.js")

FILEAPI_JS = Bundle("fileapi/FileAPI.js")

FONTAWESOME_LESS = Bundle("font-awesome/less/font-awesome.less")

REQUIRE_JS = Bundle("requirejs/require.js", "requirejs/domReady.js")

SELECT2_LESS = Bundle("select2/select2.css", "select2/select2-bootstrap.css")
SELECT2_JS = Bundle("select2/select2.js")

TYPEAHEAD_LESS = Bundle("typeahead/typeahead.js-bootstrap.less")
TYPEAHEAD_JS = Bundle("typeahead/typeahead.js", "typeahead/hogan-2.0.0.js")

ABILIAN_LESS = Bundle("less/abilian.less", "less/print.less")

es2015 = get_filter("babel", presets="es2015")

ABILIAN_JS_NS = Bundle("js/abilian-namespace.js")
ABILIAN_JS = Bundle(
    "js/abilian.js",
    "js/datatables-setup.js",
    "js/datatables-advanced-search.js",
    "js/widgets/base.js",
    "js/widgets/select2.js",
    "js/widgets/richtext.js",
    "js/widgets/file.js",
    "js/widgets/image.js",
    "js/widgets/tags.js",
    "js/widgets/dynamic-row.js",
    "js/widgets/delete.js",
)

CSS = Bundle(
    TAILWIND_CSS,
    FONTAWESOME_LESS,
    SELECT2_LESS,
    # TYPEAHEAD_LESS,
    # BOOTSTRAP_DATEPICKER_LESS,
    # BOOTSTRAP_SWITCH_LESS,
    # BOOTSTRAP_TIMEPICKER_LESS,
    # DATATABLE_LESS,
    # ABILIAN_LESS,
)

TOP_JS = Bundle(REQUIRE_JS, JQUERY, ABILIAN_JS_NS)

JS = Bundle(
    ALPINE_JS,
    TYPEAHEAD_JS,
    BOOTBOX_JS,
    SELECT2_JS,
    BOOTSTRAP_DATEPICKER_JS,
    BOOTSTRAP_SWITCH_JS,
    BOOTSTRAP_TIMEPICKER_JS,
    DATATABLE_JS,
    FILEAPI_JS,
    ABILIAN_JS,
)

JS_I18N = (
    "select2/select2_locale_{lang}.js",
    "bootstrap-datepicker/js/locales/bootstrap-datepicker.{lang}.js",
)
