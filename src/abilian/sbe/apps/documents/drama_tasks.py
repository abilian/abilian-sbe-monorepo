"""Dramatiq tasks related to dicuments."""
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from sqlalchemy.sql.functions import mode

import dramatiq
from loguru import logger
from sqlalchemy.orm import Session

from abilian.core.extensions import db
from abilian.logutils.configure import connect_logger
from abilian.services import converter, get_service
from abilian.services.conversion import ConversionError, HandlerNotFound

from pathlib import Path

if TYPE_CHECKING:
    from .models import Document

connect_logger(logger)


@dramatiq.actor
def log_document_id(document_id: int) -> None:
    """Test for dramatiq tasks

    log_document_id.send(id)
    """
    connect_logger(logger)

    msg = f"drama log doc id : {document_id}"

    path = Path("/var/tmp/test.txt")
    path.write_text(msg)

    logger.info(msg)
