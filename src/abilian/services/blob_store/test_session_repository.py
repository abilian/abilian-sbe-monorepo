""""""
from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from . import blob_store, session_blob_store
from .service import BlobStoreTransaction


def test_transaction_lifetime(session: Session):
    state = session_blob_store.app_state
    root_transaction = state.get_transaction(session)
    assert isinstance(root_transaction, BlobStoreTransaction)
    assert root_transaction._parent is None

    # create sub-transaction (db savepoint)
    session.begin(nested=True)
    transaction = state.get_transaction(session)
    assert isinstance(transaction, BlobStoreTransaction)
    assert transaction._parent is root_transaction

    session.flush()
    transaction = state.get_transaction(session)

    # FIXME
    # assert transaction is root_transaction
    #
    # # create subtransaction (sqlalchemy)
    # session.begin(subtransactions=True)
    # transaction = state.get_transaction(session)
    # assert isinstance(transaction, RepositoryTransaction)
    # assert transaction._parent is root_transaction
    #
    # session.flush()
    # transaction = state.get_transaction(session)
    # assert transaction is root_transaction


def test_accessors_non_existent_entry(session: Session):
    # non existent
    u = uuid.uuid4()
    default = Path("/xxx/dont-care")
    assert session_blob_store.get(session, u) is None
    assert session_blob_store.get(session, u, default=default) is default


def test_accessors_set_get_delete(session: Session):
    # set
    content = b"my file content"
    u1 = uuid.uuid4()
    session_blob_store.set(session, u1, content)
    path = session_blob_store.get(session, u1)
    assert isinstance(path, Path)
    assert path.open("rb").read() == content
    assert blob_store.get(u1) is None

    # delete
    session_blob_store.delete(session, u1)
    assert session_blob_store.get(session, u1) is None

    u2 = uuid.uuid4()
    blob_store.set(u2, b"existing content")
    assert session_blob_store.get(session, u2) is not None

    session_blob_store.delete(session, u2)
    assert session_blob_store.get(session, u2) is None
    assert blob_store.get(u2) is not None


def test_transaction(session: Session):
    u = uuid.uuid4()
    blob_store.set(u, b"first draft")
    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    assert path.open("rb").read() == b"first draft"

    session_blob_store.set(session, u, b"new content")

    # test nested (savepoint)
    # delete content but rollback transaction
    db_tr = session.begin(nested=True)
    session_blob_store.delete(session, u)
    assert session_blob_store.get(session, u) is None

    db_tr.rollback()
    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    assert path.open("rb").read() == b"new content"

    # delete and commit
    with session.begin(nested=True):
        session_blob_store.delete(session, u)
        assert session_blob_store.get(session, u) is None

    assert session_blob_store.get(session, u) is None
    assert blob_store.get(u) is not None

    session.commit()
    assert blob_store.get(u) is None

    # delete: now test subtransactions (sqlalchemy)
    blob_store.set(u, b"first draft")
    db_tr = session.begin(subtransactions=True)
    session_blob_store.delete(session, u)
    assert session_blob_store.get(session, u) is None

    db_tr.rollback()
    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    assert path.open("rb").read() == b"first draft"

    session.rollback()

    with session.begin(subtransactions=True):
        session_blob_store.delete(session, u)
        assert session_blob_store.get(session, u) is None

    assert session_blob_store.get(session, u) is None
    assert blob_store.get(u) is not None

    session.commit()
    assert blob_store.get(u) is None

    # now test 'set'
    session_blob_store.set(session, u, b"new content")
    session.commit()
    assert blob_store.get(u) is not None

    # test "set" in two nested transactions. This tests a specific code
    # branch, when a subtransaction overwrite data set in parent
    # transaction
    with session.begin(nested=True):
        session_blob_store.set(session, u, b"transaction 1")

        with session.begin(nested=True):
            session_blob_store.set(session, u, b"transaction 2")

        path = session_blob_store.get(session, u)
        assert isinstance(path, Path)
        assert path.open("rb").read() == b"transaction 2"


def test_transaction_path(session: Session):
    """Test RepositoryTransaction create storage only when needed."""
    u = uuid.uuid4()

    state = session_blob_store.app_state
    root_transaction = state.get_transaction(session)

    # assert not root_transaction.path.exists()

    with session.begin(subtransactions=True):
        transaction = state.get_transaction(session)
        assert not transaction.path.exists()

        session_blob_store.set(session, u, b"my file content")
        assert transaction.path.exists()

    assert root_transaction.path.exists()

    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    content = path.open("rb").read()
    assert content == b"my file content"
    assert root_transaction.path.exists()
