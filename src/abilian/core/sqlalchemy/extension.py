# Copyright (c) 2012-2024, Abilian SAS

"""Additional data types for sqlalchemy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flask_sqlalchemy import SQLAlchemy as SAExtension

if TYPE_CHECKING:
    from flask import Flask
    from sqlalchemy.engine.url import URL


class SQLAlchemy(SAExtension):
    """Base subclass of :class:`flask_sqlalchemy.SQLAlchemy`.

    Add our custom driver hacks.
    """

    def apply_driver_hacks(self, app: Flask, info: URL, options: dict[str, Any]):
        super().apply_driver_hacks(app, info, options)

        if info.drivername == "sqlite":
            connect_args = options.setdefault("connect_args", {})

            if "isolation_level" not in connect_args:
                # required to support savepoints/rollback without error. It disables
                # implicit BEGIN/COMMIT statements made by pysqlite (a COMMIT kills all
                # savepoints made).
                connect_args["isolation_level"] = None

        elif info.drivername.startswith("postgres"):
            options.setdefault("client_encoding", "utf8")
