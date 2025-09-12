# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

import sqlite3
from typing import Any

import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.pool
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.event import listens_for


@listens_for(sa.pool.Pool, "checkout")
def ping_connection(
    dbapi_connection: Connection, connection_record, connection_proxy
) -> None:
    """Ensure connections are valid.

    From: `http://docs.sqlalchemy.org/en/rel_0_8/core/pooling.html`

    In case db has been restarted pool may return invalid connections.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception as e:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise sa.exc.DisconnectionError from e
    cursor.close()


#
# Make Sqlite a bit more well-behaved.
#
@sa.event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    if isinstance(dbapi_connection, sqlite3.Connection):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
