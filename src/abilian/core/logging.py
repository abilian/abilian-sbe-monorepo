from __future__ import annotations

import logging
import sys

from flask import Flask
from loguru import logger


def init_logging(app: Flask) -> None:
    init_loguru(app)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def init_loguru(app: Flask):
    # register loguru as (sole) handler
    # level = app.config.get('LOG_LEVEL', 'INFO')
    if app.debug:
        level = "DEBUG"
    else:
        level = "INFO"

    set_loguru_config(level)

    app.logger.handlers = []
    app.logger.addHandler(InterceptHandler())
    logger.info("Loguru initialized")


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
