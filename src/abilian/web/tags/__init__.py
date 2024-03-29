""""""

from __future__ import annotations

from flask import Flask

# from .criterion import TagCriterion
from .extension import TagsExtension

# __all__ = ["TagCriterion", "TagsExtension"]
__all__ = ["TagsExtension"]


def register_plugin(app: Flask):
    TagsExtension(app)
