"""Create an application instance."""

from __future__ import annotations

import sys

sys.path = ["src", *sys.path]

from abilian.sbe.app import create_app  # noqa: E402

app = create_app()
