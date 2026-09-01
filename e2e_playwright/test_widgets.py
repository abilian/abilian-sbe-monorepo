# Copyright (c) 2012-2024, Abilian SAS

"""The widget layer: the plugins the pages actually depend on.

test_front_end.py checks that scripts load and pages raise no errors. That is
not the same as the widgets working -- a rich-text field can render as a plain
textarea, and a chart as an empty div, with the console perfectly clean.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Page

COMMUNITY = "e2e-community"


def test_dashboard_charts_render(logged_in: Page, base_url: str) -> None:
    """nvd3 is fetched on demand by the AMD shim, then draws into the page.

    d3 and nvd3 are 1.4MB together, so the shim loads them on first require()
    rather than on every page. Nothing else exercises that path.
    """
    logged_in.goto(f"{base_url}/admin/dashboard", wait_until="networkidle")

    # The shim resolves 'nvd3' to window.nv, after loading d3 first.
    logged_in.wait_for_function("() => typeof window.nv !== 'undefined'", timeout=15_000)
    assert logged_in.evaluate("typeof window.d3") != "undefined", "d3 never loaded"

    chart = logged_in.locator(".d3-chart svg").first
    chart.wait_for(state="attached", timeout=15_000)
    assert chart.locator("g").count() > 0, "nvd3 drew nothing into the chart"


def test_richtext_editor_loads(logged_in: Page, base_url: str) -> None:
    """CKEditor is the shim's other lazy module, and 664KB on its own."""
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/forum/new_thread/",
        wait_until="networkidle",
    )

    if logged_in.locator('[data-init-with="richtext"]').count() == 0:
        pytest.skip("no rich-text widget on this form")

    logged_in.wait_for_function(
        "() => typeof window.CKEDITOR !== 'undefined'", timeout=20_000
    )
    # The widget replaces its textarea with an editor instance.
    logged_in.wait_for_function(
        "() => window.CKEDITOR && Object.keys(window.CKEDITOR.instances).length > 0",
        timeout=20_000,
    )


def test_navbar_renders_the_search_box(logged_in: Page, base_url: str) -> None:
    """The navbar gates its search box on the search plugin being registered.

    It tested `app.APP_PLUGINS`, an attribute that exists nowhere in the
    codebase, so the box never rendered on any page.

    Whether typeahead then upgrades the input is not asserted: abilian.js builds
    its datasets from Abilian.api.search.object_types, which is empty until
    something is indexed.
    """
    logged_in.goto(f"{base_url}/social/", wait_until="networkidle")

    box = logged_in.locator("#search-box")
    assert box.count() > 0, "the navbar search box did not render"
    # Two of them: the desktop navbar and the mobile menu.
    form = logged_in.locator('form[role="search"]').first
    assert "search" in (form.get_attribute("action") or ""), (
        "the search box does not submit to the search endpoint"
    )
    assert logged_in.evaluate("typeof window.jQuery.fn.typeahead") == "function", (
        "typeahead never registered on jQuery"
    )


def test_file_input_widget_initialises(logged_in: Page, base_url: str) -> None:
    """FileAPI backs every attachment field; widgets/file.js binds it."""
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/forum/new_thread/",
        wait_until="networkidle",
    )

    if logged_in.locator(".js-fileapi-wrapper").count() == 0:
        pytest.skip("no file input on this form")

    assert logged_in.evaluate("typeof window.FileAPI") != "undefined", (
        "FileAPI never loaded"
    )
    assert logged_in.locator('.js-fileapi-wrapper input[type="file"]').count() > 0


def test_delete_confirmation_opens(logged_in: Page, base_url: str) -> None:
    """folder.js builds a confirmation listing the selected items.

    This threw "$.fn.modal is not defined" until bootbox was replaced: it
    drove Bootstrap's jQuery modal plugin, which went with Bootstrap's JS, so
    every destructive action silently did nothing.
    """
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    checkbox = logged_in.locator('input[name="object-selected"]').first
    if checkbox.count() == 0:
        pytest.skip("nothing in the folder to delete")
    checkbox.check()

    delete_button = logged_in.locator('button[value="delete"]').first
    if delete_button.count() == 0:
        pytest.skip("no delete button on the listing")
    delete_button.click()

    dialog = logged_in.locator("dialog[open]")
    dialog.wait_for(state="visible", timeout=10_000)
    assert dialog.locator("ul.folder-items li").count() > 0, (
        "the confirmation did not list the selected items"
    )


def test_alpine_collapse_plugin_is_registered(
    logged_in: Page, base_url: str
) -> None:
    """x-collapse is used in four templates, and did nothing for a while.

    @alpinejs/collapse was never installed, so Alpine silently ignored the
    directive. An unregistered directive is inert rather than noisy, so ask
    Alpine directly instead of waiting for an error that never comes.
    """
    logged_in.goto(
        f"{base_url}/communities/{COMMUNITY}/docs/", wait_until="networkidle"
    )

    assert logged_in.evaluate("typeof window.Alpine") != "undefined", "Alpine missing"
    registered = logged_in.evaluate(
        "() => !!window.Alpine.directives || "
        "typeof window.Alpine.directive === 'function'"
    )
    assert registered, "Alpine exposes no directive registry"
    # Build the probe with the DOM API: an x-collapse element Alpine has not
    # been taught about keeps its inline height untouched.
    took_effect = logged_in.evaluate("""() => {
      const host = document.createElement("div");
      host.setAttribute("x-data", "{ open: false }");
      const inner = document.createElement("span");
      inner.setAttribute("x-show", "open");
      inner.setAttribute("x-collapse", "");
      host.appendChild(inner);
      document.body.appendChild(host);
      window.Alpine.initTree(host);
      const styled = inner.style.height !== "" || inner.style.display === "none";
      host.remove();
      return styled;
    }""")
    assert took_effect, (
        "x-collapse had no effect: @alpinejs/collapse is not registered"
    )
