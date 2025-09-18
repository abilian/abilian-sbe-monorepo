# Copyright (c) 2012-2024, Abilian SAS

"""
Vite integration for Flask - replaces Flask-Assets
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flask import current_app, url_for

if TYPE_CHECKING:
    from abilian.app import Application


class ViteAssetManager:
    """Simple Vite asset manager to replace Flask-Assets"""

    def __init__(self, app=None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Application) -> None:
        """Initialize Vite asset manager with Flask app"""
        app.jinja_env.globals["vite_asset"] = self.asset_url
        app.jinja_env.globals["vite_dev_server"] = self.is_dev_server_running

        # Add static URL for Vite built assets
        vite_dist_path = Path(app.root_path).parent.parent / "vite" / "dist"
        if vite_dist_path.exists():
            app.add_static_url("vite", str(vite_dist_path), endpoint="vite_static")

        # Initialize legacy assets for favicons and other static resources
        from abilian.web import assets as legacy_assets

        legacy_assets.init_app(app)

    def asset_url(self, path: str) -> str:
        """Get URL for a Vite asset"""
        if self.is_dev_server_running():
            # Development mode - use Vite dev server
            return f"http://localhost:5173/src/{path}"
        # Production mode - use built assets
        return url_for("vite_static", filename=path)

    def is_dev_server_running(self) -> bool:
        """Check if Vite dev server is running"""
        # In development, check if we have the dev flag or if the dev server is accessible
        return current_app.debug

    def get_css_assets(self) -> list[str]:
        """Get list of CSS assets to include"""
        if self.is_dev_server_running():
            return ["styles.css"]  # This will be transformed by Vite dev server
        return ["styles.css"]  # Built asset

    def get_js_assets(self) -> list[str]:
        """Get list of JS assets to include"""
        # For now, we're just serving Alpine.js via CDN
        return []


def init_app(app: Application) -> None:
    """Initialize Vite integration"""
    vite_manager = ViteAssetManager(app)
    app.extensions["vite"] = vite_manager
