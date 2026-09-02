# Copyright (c) 2012-2024, Abilian SAS

"""Capture the same pages from an instance, for visual comparison.

Run once against the baseline (the pre-migration UI, served by baseline.sh) and
once against the current branch, then compare the pairs:

    uv run --with pytest-playwright python e2e_playwright/capture.py \\
        https://127.0.0.1:8898 shots/baseline
    uv run --with pytest-playwright python e2e_playwright/capture.py \\
        http://127.0.0.1:8899 shots/current

Both instances run the same seed data, so any difference is the front end.
"""

from __future__ import annotations

import os
import pathlib
import sys

from playwright.sync_api import sync_playwright

COMMUNITY = "e2e-community"
EMAIL = os.environ.get("E2E_EMAIL", "admin@example.com")
PASSWORD = os.environ.get("E2E_PASSWORD", "e2e-password")

#: name -> path. Anonymous pages first, then the rest with a session.
ANONYMOUS = {
    "login": "/user/login",
}

PAGES = {
    "wall": f"/communities/{COMMUNITY}/wall/",
    "docs": f"/communities/{COMMUNITY}/docs/",
    "forum": f"/communities/{COMMUNITY}/forum/",
    "forum-new-thread": f"/communities/{COMMUNITY}/forum/new_thread/",
    "wiki": f"/communities/{COMMUNITY}/wiki/",
    "members": f"/communities/{COMMUNITY}/members",
    "communities": "/communities/",
    "social": "/social/",
    "preferences": "/preferences/",
    "admin-dashboard": "/admin/dashboard",
    "admin-users": "/admin/users",
    "admin-groups": "/admin/groups",
    "admin-audit": "/admin/audit",
    "admin-settings": "/admin/settings",
}

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 375, "height": 812},
}


def capture(base_url: str, out_dir: pathlib.Path, viewport_name: str) -> None:
    viewport = VIEWPORTS[viewport_name]
    out = out_dir / viewport_name
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport=viewport, ignore_https_errors=True)
        page = context.new_page()

        for name, path in ANONYMOUS.items():
            page.goto(f"{base_url}{path}", wait_until="networkidle")
            page.screenshot(path=out / f"{name}.png", full_page=True)

        page.goto(f"{base_url}/user/login", wait_until="networkidle")
        page.fill('input[name="email"]', EMAIL)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        for name, path in PAGES.items():
            try:
                page.goto(f"{base_url}{path}", wait_until="networkidle", timeout=30_000)
                page.screenshot(path=out / f"{name}.png", full_page=True)
            except Exception as exc:
                print(f"  !! {viewport_name}/{name}: {type(exc).__name__}")

        browser.close()

    print(f"  {viewport_name}: {len(list(out.glob('*.png')))} shots -> {out}")


if __name__ == "__main__":
    base = sys.argv[1].rstrip("/")
    target = pathlib.Path(sys.argv[2])
    for vp in sys.argv[3:] or ["desktop"]:
        capture(base, target, vp)
