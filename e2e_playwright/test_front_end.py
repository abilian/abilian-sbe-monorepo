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


EXISTING_FOLDER = "Existing Folder"


def test_duplicate_folder_name_is_rejected(logged_in: Page, base_url: str) -> None:
    """folder_edit.js checks the title before letting the form submit.

    It had been inert since the Tailwind conversion: it bound to
    `button.btn-primary`, a class the converted modals no longer carry, and
    toggled `hide`, a Bootstrap class that no longer exists.
    """
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    logged_in.locator('[href="#modal-new-folder"]').first.click()
    modal = logged_in.locator("#modal-new-folder")
    assert modal.is_visible(), "the new-folder modal did not open"

    modal.locator('input[name="title"]').fill(EXISTING_FOLDER)
    modal.locator('button[type="submit"]').click()

    help_text = modal.locator("span.help-block")
    help_text.wait_for(state="visible", timeout=5_000)
    assert EXISTING_FOLDER in help_text.inner_text(), (
        f"expected a duplicate-name error, got {help_text.inner_text()!r}"
    )
    # The modal must still be open: the submit was blocked.
    assert modal.is_visible()


def test_gallery_view_shares_the_folder_behaviour(
    logged_in: Page, base_url: str, js_errors: JSErrors
) -> None:
    """The gallery view runs the same module as the table view.

    folder.js and folder_gallery.js were near-duplicates; the gallery is now the
    shared half of one module, so it needs its own exercise.
    """
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    logged_in.locator('button[name="view_style"][value="gallery_view"]').first.click()
    logged_in.wait_for_load_state("networkidle")

    js_errors.assert_clean("the gallery view")
    assert logged_in.evaluate("typeof window.SBEFolderGalleryListingSetup") == (
        "function"
    ), "the gallery module never defined itself"
    # Shared with the table view, and the reason the two files existed.
    assert logged_in.evaluate("typeof window.SBEFolderCommonSetup") == "function"
