"""
TODO: move somewhere else, this is not a setup module.

"""

from flask import Flask, g, request

from abilian.web.nav import BreadcrumbItem


def setup_nav_and_breadcrumbs(app: Flask):
    """Listener for `request_started` event.

    If you want to customize first items of breadcrumbs, override
    :meth:`init_breadcrumbs`
    """
    g.nav = {"active": None}  # active section
    g.breadcrumb = []
    init_breadcrumbs()


def init_breadcrumbs():
    """Insert the first element in breadcrumbs.

    This happens during `request_started` event, which is triggered
    before any url_value_preprocessor and `before_request` handlers.
    """
    g.breadcrumb.append(BreadcrumbItem(icon="home", url=f"/{request.script_root}"))
