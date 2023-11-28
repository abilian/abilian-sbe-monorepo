"""Dramatiq tasks related to dicuments."""
import dramatiq
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from abilian.core.extensions import db
from abilian.services import converter, get_service
from abilian.services.conversion import ConversionError, HandlerNotFound

if TYPE_CHECKING:
    from .models import Document

logger = logging.getLogger(__package__)


@dramatiq.actor
def log_document_id(document_id: int) -> None:
    """Test for dramatiq tasks

    log_document_id.send(id)
    """
    msg = f"drama log doc id : {document_id}"
    logger.info(msg)


# @shared_task
# def process_document(document_id: int) -> None:
#     """Run document processing chain."""
#     with get_document(document_id) as (session, document):
#         if document is None:
#             return

#         # True = Ok, None means no check performed (no antivirus present)
#         is_clean = _run_antivirus(document)
#         if is_clean is False:
#             return

#     preview_document.delay(document_id)
#     convert_document_content.delay(document_id)
