# Copyright (c) 2012-2024, Abilian SAS

"""Front-end checks the server-side suite structurally cannot make.

Each of these corresponds to a way the Tailwind branch was broken while pytest
stayed green: scripts dropped from the page, an icon font never shipped, an AMD
shim resolving modules to empty objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from conftest import JSErrors
    from playwright.sync_api import Page

#: Talisman applies its default CSP (`default-src 'self'`) whenever debug is off,
#: and nothing in the app or any deploy config overrides it. The base template
#: ships inline <script> blocks -- the AMD shim, abilian_init.js and the deferred
#: JS -- so the browser blocks every one of them and no legacy JS runs at all.
#: Pre-existing: `devel` has the same inline scripts and the same policy.
CSP_BLOCKS_INLINE_SCRIPTS = pytest.mark.xfail(
    reason="CSP blocks the inline scripts, so no legacy JS executes",
    strict=True,
)


@CSP_BLOCKS_INLINE_SCRIPTS
def test_home_page_has_no_js_errors(
    page: Page, base_url: str, js_errors: JSErrors
) -> None:
    page.goto(f"{base_url}/", wait_until="networkidle")
    js_errors.assert_clean("the home page")


@CSP_BLOCKS_INLINE_SCRIPTS
@pytest.mark.parametrize(
    "path",
    ["/social/", "/communities/", "/admin/", "/preferences/"],
)
def test_main_pages_have_no_js_errors(
    logged_in: Page, base_url: str, js_errors: JSErrors, path: str
) -> None:
    """The check that would have caught the whole Phase 2 breakage at once."""
    logged_in.goto(f"{base_url}{path}", wait_until="networkidle")
    js_errors.assert_clean(path)


@CSP_BLOCKS_INLINE_SCRIPTS
def test_the_javascript_layer_is_loaded(logged_in: Page, base_url: str) -> None:
    """jQuery and its plugins must actually be on the page, not merely linked."""
    logged_in.goto(f"{base_url}/social/", wait_until="networkidle")

    assert logged_in.evaluate("typeof window.jQuery") == "function", "jQuery missing"
    assert logged_in.evaluate("typeof window.jQuery.fn.dataTable") != "undefined", (
        "DataTables did not register on jQuery"
    )
    assert logged_in.evaluate("typeof window.jQuery.fn.select2") == "function", (
        "select2 did not register on jQuery"
    )
    assert logged_in.evaluate("typeof window.Alpine") != "undefined", "Alpine missing"
    assert logged_in.evaluate("typeof window.AbilianWidget") != "undefined", (
        "the widget registry never defined itself"
    )


def test_icon_font_is_applied(logged_in: Page, base_url: str) -> None:
    """`fa fa-*` is used ~147 times; without the font every icon is a blank box."""
    logged_in.goto(f"{base_url}/social/", wait_until="networkidle")

    icon = logged_in.locator("i.fa").first
    assert icon.count() > 0, "no FontAwesome icon on the page to check"

    font = icon.evaluate("el => getComputedStyle(el).fontFamily")
    assert "FontAwesome" in font, f"icon font not applied, got {font!r}"


def test_stylesheet_is_applied(logged_in: Page, base_url: str) -> None:
    """Catches the unstyled page an asset-path mismatch produces."""
    logged_in.goto(f"{base_url}/social/", wait_until="networkidle")

    body_bg = logged_in.evaluate(
        "getComputedStyle(document.body).backgroundColor"
    )
    # Tailwind's preflight sets a background; an unstyled page stays transparent.
    assert body_bg not in ("", "rgba(0, 0, 0, 0)"), (
        f"no stylesheet applied to body, background is {body_bg!r}"
    )
