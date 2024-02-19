""""""

from __future__ import annotations

import uuid
from pathlib import Path
import pytest

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
    current_transaction = state.get_transaction(session)

    # FIXME: fixed, see explanation:
    # when sqlalchemy is flushing it is done in a sub-transaction,
    # not the root one. So when calling our 'commit' from here
    # we are not in our root transaction, so changes will not be
    # written to repository.
    # assert transaction is root_transaction

    assert current_transaction is transaction

    # # create subtransaction (sqlalchemy)
    session.begin(subtransactions=True)
    current_transaction = state.get_transaction(session)
    assert isinstance(current_transaction, BlobStoreTransaction)
    assert current_transaction._parent is transaction

    session.flush()
    current_transaction = state.get_transaction(session)
    assert current_transaction._parent is transaction


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
    assert path.read_bytes() == b"first draft"

    # same uuid, changed content
    session_blob_store.set(session, u, b"new content")

    # test nested (savepoint)
    # delete content but rollback transaction
    db_tr = session.begin(nested=True)
    session_blob_store.delete(session, u)
    assert session_blob_store.get(session, u) is None

    db_tr.rollback()
    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    assert path.read_bytes() == b"new content"

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
    assert path.read_bytes() == b"first draft"

    session.rollback()

    session_blob_store.show_g(1)

    with session.begin(subtransactions=True):
        session_blob_store.delete(session, u)
        assert session_blob_store.get(session, u) is None
        session_blob_store.show_g(2)

    session_blob_store.show_g(3)

    assert session_blob_store.get(session, u) is None
    assert blob_store.get(u) is not None

    path = blob_store.get(u)
    assert isinstance(path, Path)
    assert path.read_bytes() == b"first draft"

    session_blob_store.show_g(31)

    session.commit()
    session_blob_store.show_g(32)
    # IMPORTANT: now the transaction stored in g due to the commit.
    # so the session_blob_store.get will return None
    assert session_blob_store.get(session, u) is None

    assert blob_store.get(u) is None

    # now test 'set'

    session_blob_store.show_g(4)

    state = session_blob_store.app_state
    state.create_transaction(session, None)

    session_blob_store.show_g(6)

    session_blob_store.set(session, u, b"new content")
    session_blob_store.show_g(61)
    session.commit()
    session_blob_store.show_g(62)
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
        assert not transaction.tmp_folder.exists()

        session_blob_store.set(session, u, b"my file content")
        assert transaction.tmp_folder.exists()

    assert root_transaction.tmp_folder.exists()

    path = session_blob_store.get(session, u)
    assert isinstance(path, Path)
    content = path.open("rb").read()
    assert content == b"my file content"
    assert root_transaction.tmp_folder.exists()
