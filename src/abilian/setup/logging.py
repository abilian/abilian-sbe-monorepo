# Copyright (c) 2012-2024, Abilian SAS

# ruff: noqa: PLC0415

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from flask import Flask


def init_logging(app: Flask) -> None:
    run_from_cli = app.config.get("RUN_FROM_CLI")

    if run_from_cli and not app.debug:
        print("Running from CLI, skipping logging init (use --debug to enable)")
        logger.configure(handlers=[])
    else:
        init_loguru(app)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def init_loguru(app: Flask):
    """Register loguru as (sole) handler."""
    if app.debug:
        level = "DEBUG"
    else:
        level = "INFO"

    logger.remove()
    logger.add(sys.stderr, level=level)

    app.logger.handlers = [InterceptHandler()]
    logger.info("Loguru initialized")
