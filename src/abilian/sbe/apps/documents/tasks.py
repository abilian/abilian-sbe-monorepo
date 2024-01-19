"""Dramatiq tasks related to documents."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy.orm import Session

from abilian.core.dramatiq.singleton import dramatiq
from abilian.core.extensions import db
from abilian.services import converter, get_service
from abilian.services.conversion import ConversionError, HandlerNotFound

if TYPE_CHECKING:
    from .models import Document


@contextmanager
def get_document(
    document_id: int, session: Session | None = None
) -> Iterator[tuple[Session, Document | None]]:
    """Context manager that yields (session, document)."""
    from .models import Document

    #
    logger.info(f"get_document() {document_id=} {session=}")

    if session is None:
        doc_session = db.create_scoped_session()
    else:
        doc_session = session

    with doc_session.begin_nested():
        query = doc_session.query(Document)
        document = query.get(document_id)
        logger.debug(f"get_document() {document=} {session=}")
        yield (doc_session, document)

    # cleanup
    if session is None:
        doc_session.commit()
        doc_session.close()


@dramatiq.actor(max_retries=20, max_backoff=86400000)
def process_document(document_id: int) -> None:
    """Task to process a document.

    max_retries = 20 (Dramatiq default)
    max_backoff = 86400000 , i.e. 1 day
    """
    logger.info(f"process_document() actor : {document_id=}")

    with get_document(document_id) as (session, document):
        if document is None:
            return

        # True = Ok, None means no check performed (no antivirus present)
        is_clean = _run_antivirus(document)
        logger.debug(f"process_document() {document_id=} {is_clean=}")
        if is_clean is False:
            return
    logger.debug(f"process_document() virus clean {document_id=}")
    preview_document.send(document_id)
    logger.debug(f"process_document() before convert_document_content {document_id=}")
    convert_document_content.send(document_id)
    logger.debug(f"process_document() exit {document_id=}")


def _run_antivirus(document: Document) -> bool | None:
    antivirus = get_service("antivirus")
    if antivirus and antivirus.running:
        is_clean = antivirus.scan(document.content_blob)
        if "antivirus_task" in document.content_blob.meta:
            del document.content_blob.meta["antivirus_task"]
        return is_clean
    return None


@dramatiq.actor
def antivirus_scan(document_id):
    """Return antivirus.scan() result."""
    with get_document(document_id) as (session, document):
        if document is None:
            return None
        return _run_antivirus(document)


@dramatiq.actor(max_retries=5)
def preview_document(document_id: int) -> None:
    """Compute the document preview images with its default preview size."""

    logger.info(f"preview_document() {document_id=}")

    with get_document(document_id) as (session, document):
        logger.debug(f"preview_document() {document_id=} {document=}")
        if document is None:
            # deleted after task queued, but before task run
            return

        convert_to_image(document)


@logger.catch(level="ERROR")
def convert_to_image(doc: Document) -> None:
    logger.info(f"convert_to_image() {doc=}")

    try:
        converter.to_image(
            doc.content_digest,
            doc.content,
            doc.content_type,
            0,
            doc.preview_size,
        )
    except ConversionError as e:
        logger.info(f"Preview failed for document {doc.name}: {e}")


@dramatiq.actor(max_retries=5)
def convert_document_content(document_id: int) -> None:
    """Convert document content."""

    logger.info(f"convert_document_content() {document_id=}")

    with get_document(document_id) as (session, doc):
        if doc is None:
            # deleted after task queued, but before task run
            return

        convert_to_pdf(doc)
        convert_to_text(doc)
        extract_metadata(doc)


@logger.catch(level="ERROR")
def convert_to_pdf(doc: Document) -> None:
    logger.info(f"convert_to_pdf() {doc=}")

    if doc.content_type == "application/pdf":
        doc.pdf = doc.content
        return
    try:
        doc.pdf = converter.to_pdf(doc.content_digest, doc.content, doc.content_type)
    except (HandlerNotFound, ConversionError) as e:
        doc.pdf = b""
        logger.info(f"Conversion to PDF failed for document {doc.name}: {e}")


@logger.catch(level="ERROR")
def convert_to_text(doc: Document) -> None:
    logger.info(f"convert_to_text() {doc=}")

    try:
        doc.text = converter.to_text(doc.content_digest, doc.content, doc.content_type)
    except ConversionError as e:
        doc.text = ""
        logger.info(f"Conversion to text failed for document {doc.name}: {e}")


@logger.catch(level="ERROR")
def extract_metadata(doc: Document) -> None:
    logger.info(f"extract_metadata() {doc=}")

    doc.extra_metadata = {}
    try:
        doc.extra_metadata = converter.get_metadata(
            doc.content_digest, doc.content, doc.content_type
        )
    except ConversionError as e:
        logger.warning(f"Metadata extraction failed on document {doc.name}: {e}")
    except UnicodeDecodeError as e:
        logger.error(f"Unicode issue on document {doc.name}: {e}")
    except Exception as e:
        logger.error(f"Other issue on document {doc.name}: {e}")

    if doc.text:
        import langid

        doc.language = langid.classify(doc.text)[0]

    doc.page_num = doc.extra_metadata.get("PDF:Pages", 1)
