from __future__ import annotations

import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
DB_URIS = [
    "sqlite:///test.db",
    # TODO: Postgres & MariaDB
]
nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.run("uv", "sync")
    session.run("uv", "pip", "check")
    session.run("uv", "run", "make", "lint")
    session.run("uv", "pip", "install", "safety", "pip-audit")
    session.run("uv", "run", "adt", "audit")


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.run("uv", "sync")
    session.run("uv", "run", "pytest", "--tb=short")


@nox.session
@nox.parametrize("db_uri", DB_URIS)
def db_test(session: nox.Session, db_uri: str) -> None:
    env = {
        "FLASK_SQLALCHEMY_DATABASE_URI": db_uri,
    }
    session.run("uv", "sync")
    session.run("uv", "run", "pytest", "--tb=short", env=env)
