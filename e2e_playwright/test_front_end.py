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


def test_home_page_has_no_js_errors(
    page: Page, base_url: str, js_errors: JSErrors
) -> None:
    page.goto(f"{base_url}/", wait_until="networkidle")
    js_errors.assert_clean("the home page")


@pytest.mark.parametrize(
    "path",
    [
        "/social/",
        "/communities/",
        "/preferences/",
        # The dashboard exercises the shim's lazy loader (d3 + nvd3, 1.4MB).
        "/admin/dashboard",
        # A DataTables listing with a select2 filter.
        "/admin/users",
    ],
)
def test_main_pages_have_no_js_errors(
    logged_in: Page, base_url: str, js_errors: JSErrors, path: str
) -> None:
    """The check that would have caught the whole Phase 2 breakage at once."""
    logged_in.goto(f"{base_url}{path}", wait_until="networkidle")
    js_errors.assert_clean(path)


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


#: Seeded by seed.py, which serve.sh runs before starting the app.
COMMUNITY = "e2e-community"


@pytest.mark.parametrize("app_path", ["wall", "docs", "forum", "wiki"])
def test_community_apps_have_no_js_errors(
    logged_in: Page, base_url: str, js_errors: JSErrors, app_path: str
) -> None:
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/{app_path}/", wait_until="networkidle"
    )
    js_errors.assert_clean(f"/communities/{COMMUNITY}/{app_path}/")


def test_folder_listing_initialises_its_datatable(
    logged_in: Page, base_url: str
) -> None:
    """The documents listing is the most intricate page in the app.

    Its DataTable, sorting and select-all come from folder.js, which the branch
    had commented out entirely; server-side nothing noticed, because the page
    still rendered.
    """
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    assert logged_in.locator("#objects-table").count() > 0, "no folder listing table"
    # DataTables wraps the table once it has initialised.
    assert logged_in.locator(".dataTables_wrapper").count() > 0, (
        "DataTables never initialised on the folder listing"
    )


def test_a_modal_opens(logged_in: Page, base_url: str) -> None:
    """initModals() binds data-toggle="modal"; ModalActionMixin emits it."""
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    trigger = logged_in.locator('[data-toggle="modal"]').first
    if trigger.count() == 0:
        pytest.skip("no modal trigger on the folder listing")

    target = trigger.get_attribute("href") or trigger.get_attribute("data-target")
    trigger.click()

    modal = logged_in.locator(target)
    assert modal.is_visible(), f"clicking the trigger did not open {target}"
