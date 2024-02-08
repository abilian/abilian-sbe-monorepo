from __future__ import annotations

import logging
import sys

from flask import Flask
from loguru import logger

# Note: prior `patch_logger` feature is now replaced by a simple call to
# loguru, using loguru.trace(). So, by defaut
#
#


def init_logging(app: Flask) -> None:
    run_from_cli = app.config.get("RUN_FROM_CLI")
    if run_from_cli and not app.debug:
        print("Running from CLI, skipping logging init (use --debug to enable)")
        logger.remove()
        intercept_logging_library(app)
    else:
        init_loguru(app)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def intercept_logging_library(app: Flask) -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    app.logger.handlers = []
    app.logger.addHandler(InterceptHandler())


def init_loguru(app: Flask):
    # register loguru as (sole) handler
    level = app.config.get("LOG_LEVEL")
    if not level:
        if app.debug:
            level = "DEBUG"
        else:
            level = "INFO"

    set_loguru_config(level)
    intercept_logging_library(app)
    logger.debug("Loguru initialized")


def set_loguru_config(level: str = "DEBUG"):
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,
    )
