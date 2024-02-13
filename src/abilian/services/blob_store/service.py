from __future__ import annotations

import contextlib
import shutil
import typing
import weakref
from pathlib import Path
from typing import IO, Any
from uuid import UUID, uuid1

from flask import g
import sqlalchemy as sa

# import sqlalchemy.event
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session, SessionTransaction
from sqlalchemy.orm.unitofwork import UOWTransaction

from abilian.core.extensions import db
from abilian.core.models import Model
from abilian.core.models.blob import Blob
from abilian.services import Service, ServiceState

if typing.TYPE_CHECKING:
    from abilian.app import Application

_NULL_MARK = object()


def _assert_uuid(uuid: Any):
    if not isinstance(uuid, UUID):
        raise TypeError("Not an uuid.UUID instance", uuid)


class BlobStoreServiceState(ServiceState):
    #: :class:`Path` path to application repository
    path: Path | None = None


class BlobStoreService(Service):
    """Service for storage of binary objects referenced in database."""

    name = "blob_store"
    AppStateClass = BlobStoreServiceState

    def init_app(self, app: Application):
        super().init_app(app)

        path = app.data_dir / "files"
        if not path.exists():
            path.mkdir(mode=0o775, parents=True)

        with app.app_context():
            self.app_state.path = path.resolve()

    # data management: paths and accessors
    def rel_path(self, uuid: UUID) -> Path:
        """Contruct relative path from blob store top directory to the file
        named after this uuid.

        :param:uuid: :class:`UUID` instance
        """
        _assert_uuid(uuid)

        filename = str(uuid)
        return Path(filename[0:2], filename[2:4], filename)

    def abs_path(self, uuid: UUID) -> Path:
        """Return absolute :class:`Path` object for given uuid.

        :param:uuid: :class:`UUID` instance
        """
        _assert_uuid(uuid)

        top = self.app_state.path
        rel_path = self.rel_path(uuid)
        dest = top / rel_path
        assert top in dest.parents
        return dest

    def get(self, uuid: UUID, default: Path | None = None) -> Path | None:
        """Return absolute :class:`Path` object for given uuid, if this uuid
        exists in blob store, or `default` if it doesn't.

        :param:uuid: :class:`UUID` instance
        """
        _assert_uuid(uuid)

        path = self.abs_path(uuid)
        if not path.exists():
            return default
        return path

    def set(self, uuid: UUID, content: Any, encoding: str | None = "utf-8"):
        """Store binary content with uuid as key.

        :param:uuid: :class:`UUID` instance
        :param:content: string, bytes, or any object with a `read()` method
        :param:encoding: encoding to use when content is Unicode
        """
        _assert_uuid(uuid)

        dest = self.abs_path(uuid)
        if not dest.parent.exists():
            dest.parent.mkdir(0o775, parents=True)

        if hasattr(content, "read"):
            content = content.read()

        mode = "tw"
        if not isinstance(content, str):
            mode = "bw"
            encoding = None

        with dest.open(mode, encoding=encoding) as f:
            f.write(content)

    def delete(self, uuid: UUID):
        """Delete file with given uuid.

        :param:uuid: :class:`UUID` instance
        :raises:KeyError if file does not exists
        """
        _assert_uuid(uuid)

        dest = self.abs_path(uuid)
        if not dest.exists():
            raise KeyError("No file can be found for this uuid", uuid)

        dest.unlink()

    def __getitem__(self, uuid: UUID) -> Path:
        _assert_uuid(uuid)

        value = self.get(uuid)
        if value is None:
            raise KeyError("No file can be found for this uuid", uuid)
        return value

    def __setitem__(self, uuid: UUID, content: Any):
        _assert_uuid(uuid)

        self.set(uuid, content)

    def __delitem__(self, uuid: UUID):
        _assert_uuid(uuid)

        self.delete(uuid)


blob_store = BlobStoreService()

_BLOB_STORE_TRANSACTION = "abilian_blob_store_transactions"


class SessionBlobStoreState(ServiceState):
    path: Path

    # @property
    # def transactions(self) -> dict[int, Any]:
    #     if not hasattr(g, _BLOB_STORE_TRANSACTION):
    #         reg: dict[int, Any] = {}
    #         setattr(g, _BLOB_STORE_TRANSACTION, reg)
    #     return getattr(g, _BLOB_STORE_TRANSACTION)
    #     # try:
    #     #     return flask._lookup_app_object(_BLOB_STORE_TRANSACTION)
    #     # except AttributeError:
    #     #     reg: dict[int, Any] = {}
    #     #     setattr(flask._app_ctx_stack.top, _BLOB_STORE_TRANSACTION, reg)
    #     #     return reg

    # @transactions.setter
    # def transactions(self, reg: dict[int, Any]):
    #     setattr(g, _BLOB_STORE_TRANSACTION, reg)

    @staticmethod
    def transaction_key(session: Session | scoped_session) -> str:
        from icecream import ic

        if isinstance(session, scoped_session):
            session = session()
        session_id = id(session)
        return ic(f"blob_session_{session_id}")

    # transaction <-> db session accessors
    def get_transaction(
        self, session: Session | scoped_session
    ) -> BlobStoreTransaction | None:
        from icecream import ic

        ic("----------- get_transaction()")
        ic(session)
        if isinstance(session, scoped_session):
            ic("is scoped_session")
            session = session()
            ic("actual session", session)

        key = self.transaction_key(session)
        default = weakref.ref(session), None
        ic(default)
        session_reference, transaction = g.get(key, default)
        ic(session_reference)
        ic(transaction)
        found_session = ic(session_reference())

        # session_id = ic(id(session))
        # ic(self.transactions)
        # session_ref, transaction = self.transactions.get(session_id, default)
        # found_session = ic(session_ref())
        # ic(transaction)

        if found_session is None or found_session is not session:
            ic("# old session with same id, maybe not yet garbage collected")
            transaction = None
        return transaction

    def set_transaction(
        self,
        session: Session | scoped_session,
        transaction: BlobStoreTransaction | None,
    ) -> None:
        if isinstance(session, scoped_session):
            session = session()

        key = self.transaction_key(session)
        value = (weakref.ref(session), transaction)
        setattr(g, key, value)

        # session_id = id(session)
        # self.transactions[session_id] = (weakref.ref(session), transaction)

    def create_transaction(self, session: Session, transaction: BlobStoreTransaction):
        if not self.running:
            return

        parent = self.get_transaction(session)
        root_path = self.path
        transaction = BlobStoreTransaction(root_path, parent)
        self.set_transaction(session, transaction)

    def end_transaction(self, session: Session, transaction: BlobStoreTransaction):
        if not self.running:
            return

        tr = self.get_transaction(session)
        if tr is not None:
            if not tr.cleared:
                # root and nested transactions emit "commit", but
                # subtransactions don't
                tr.commit(session)
            self.set_transaction(session, tr._parent)

    def begin(self, session: Session):
        if not self.running:
            return

        tr = self.get_transaction(session)
        if tr is None:
            # FIXME: return or create a new one?
            return

        tr.begin(session)

    def commit(self, session: Session):
        if not self.running:
            return

        tr = self.get_transaction(session)
        if tr is None:
            return

        tr.commit(session)

    def flush(self, session: Session, flush_context: UOWTransaction):
        # when sqlalchemy is flushing it is done in a sub-transaction,
        # not the root one. So when calling our 'commit' from here
        # we are not in our root transaction, so changes will not be
        # written to repository.
        self.commit(session)

    def rollback(self, session: Session):
        if not self.running:
            return

        tr = self.get_transaction(session)
        if tr is None:
            return

        tr.rollback(session)


class SessionBlobStoreService(Service):
    """A blob store service that is session aware, i.e content is actually
    written or delete at commit time.

    All content is stored using the main :class:`BlobStoreService`.
    """

    name = "session_blob_store"
    AppStateClass = SessionBlobStoreState

    def __init__(self, *args, **kwargs):
        self.__listening = False
        super().__init__(*args, **kwargs)

    def init_app(self, app: Application):
        super().init_app(app)

        path = Path(app.instance_path, "tmp", "files_transactions")
        if not path.exists():
            path.mkdir(0o775, parents=True)

        with app.app_context():
            self.app_state.path = path.resolve()

        if not self.__listening:
            self.start_listening()

    def start_listening(self):
        self.__listening = True
        listen = sa.event.listen
        listen(Session, "after_transaction_create", self.create_transaction)
        listen(Session, "after_transaction_end", self.end_transaction)
        listen(Session, "after_begin", self.begin)
        listen(Session, "after_commit", self.commit)
        listen(Session, "after_flush", self.flush)
        listen(Session, "after_rollback", self.rollback)
        # appcontext_tearing_down.connect(self.clear_transaction, app)

    def _session_for(self, model_or_session: Model | Session) -> Session:
        """Return session instance for object parameter.

        - If parameter is a session instance, it is returned as is.

        - If parameter is a registered model instance, its session will be used.

        - If parameter is a detached model instance, or None, application scoped
          session will be used (db.session()).

        - If parameter is a scoped_session instance, a new session will be
          instaniated.
        """
        from icecream import ic

        ic("---------------- _session_for()")
        ic(model_or_session)
        if model_or_session is None:
            return db.session

        if isinstance(model_or_session, Session):
            return model_or_session

        if isinstance(model_or_session, sa.orm.scoped_session):
            return model_or_session()

        session = sa.orm.object_session(model_or_session)

        if session is None:
            return db.session

        return session

    # Blob store interface
    def get(
        self, session: Session | Blob, uuid: UUID, default: Path | None = None
    ) -> Path | None:
        # assert isinstance(session, Session)
        _assert_uuid(uuid)

        session = self._session_for(session)
        transaction = self.app_state.get_transaction(session)
        try:
            val = transaction.get(uuid)
        except KeyError:
            return default

        if val is _NULL_MARK:
            val = blob_store.get(uuid, default)

        return val

    def set(
        self,
        session: Session | Blob,
        uuid: UUID,
        content: IO | bytes | str,
        encoding: str = "utf-8",
    ):
        _assert_uuid(uuid)
        from icecream import ic

        ic("------- SessionBlobStoreService.set()")
        session = self._session_for(session)
        ic(session)
        ic(self.app_state)
        transaction = ic(self.app_state.get_transaction(session))
        if transaction is None:
            raise RuntimeError("transaction is None in blob store service")
        ic("SBS.set() transaction", transaction)
        transaction.set(uuid, content, encoding)

    def delete(self, session: Session | Blob, uuid: UUID):
        _assert_uuid(uuid)

        session = self._session_for(session)
        transaction = self.app_state.get_transaction(session)
        if self.get(session, uuid) is not None:
            transaction.delete(uuid)

    # session event handlers
    @Service.if_running
    def create_transaction(
        self, session: Session, transaction: SessionTransaction
    ) -> Any | None:
        return self.app_state.create_transaction(session, transaction)

    @Service.if_running
    def end_transaction(
        self, session: Session, transaction: SessionTransaction
    ) -> Any | None:
        return self.app_state.end_transaction(session, transaction)

    @Service.if_running
    def begin(
        self, session: Session, transaction: SessionTransaction, connection: Connection
    ) -> Any | None:
        return self.app_state.begin(session)

    @Service.if_running
    def commit(self, session: Session):
        return self.app_state.commit(session)

    @Service.if_running
    def flush(self, session: Session, flush_context: UOWTransaction):
        return self.app_state.flush(session, flush_context)

    @Service.if_running
    def rollback(self, session: Session):
        return self.app_state.rollback(session)


session_blob_store = SessionBlobStoreService()


class BlobStoreTransaction:
    def __init__(self, root_path: Path, parent: BlobStoreTransaction | None = None):
        self.path = root_path / str(uuid1())
        # if parent is not None and parent.cleared:
        #   parent = None

        self._parent = parent
        self._deleted: set[UUID] = set()
        self._set: set[UUID] = set()
        self.__cleared = False

    @property
    def cleared(self) -> bool:
        return self.__cleared

    def __del__(self):
        if not self.cleared:
            self._clear()

    def _clear(self):
        if self.__cleared:
            return

        # make sure transaction is not usable anymore
        if self.path.exists():
            shutil.rmtree(str(self.path))

        del self.path
        del self._deleted
        del self._set
        self.__cleared = True

    def begin(self, session: Session | None = None):
        if not self.path.exists():
            self.path.mkdir(0o700)

    def rollback(self, session: Session | None = None):
        self._clear()

    def commit(self, session: Session | None = None):
        """Merge modified objects into parent transaction.

        Once commited a transaction object is not usable anymore

        :param:session: current sqlalchemy Session
        """
        if self.__cleared:
            return

        if self._parent:
            # nested transaction
            self._commit_parent()
        else:
            self._commit_blob_store()
        self._clear()

    def _commit_blob_store(self):
        assert self._parent is None

        for uuid in self._deleted:
            with contextlib.suppress(KeyError):
                blob_store.delete(uuid)

        for uuid in self._set:
            content = self.path / str(uuid)
            blob_store.set(uuid, content.open("rb"))

    def _commit_parent(self):
        p = self._parent
        assert p
        p._deleted |= self._deleted
        p._deleted -= self._set

        p._set |= self._set
        p._set -= self._deleted

        if self._set:
            p.begin()  # ensure p.path exists

        for uuid in self._set:
            content_path = self.path / str(uuid)
            # content_path.replace is not available with python < 3.3.
            content_path.rename(p.path / str(uuid))

    def _add_to(self, uuid: UUID, dest: set[UUID], other: set[UUID]):
        """Add `item` to `dest` set, ensuring `item` is not present in `other`
        set."""
        _assert_uuid(uuid)
        with contextlib.suppress(KeyError):
            other.remove(uuid)
        dest.add(uuid)

    def delete(self, uuid: UUID):
        self._add_to(uuid, self._deleted, self._set)

    def set(
        self, uuid: UUID, content: IO | bytes | str, encoding: str | None = "utf-8"
    ):
        self.begin()
        self._add_to(uuid, self._set, self._deleted)

        if hasattr(content, "read"):
            content = content.read()

        if isinstance(content, bytes):
            mode = "wb"
            encoding = None
        else:
            mode = "wt"

        dest = self.path / str(uuid)
        with dest.open(mode, encoding=encoding) as f:
            f.write(content)

    def get(self, uuid: UUID) -> Any:
        if uuid in self._deleted:
            raise KeyError(uuid)

        if uuid in self._set:
            path = self.path / str(uuid)
            assert path.exists()
            return path

        if self._parent:
            return self._parent.get(uuid)

        return _NULL_MARK
