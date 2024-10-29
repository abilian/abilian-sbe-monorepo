import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.install("uv")
    session.run("uv", "sync", "--inexact")
    session.run("uv", "pip", "check")
    session.run("uv", "run", "make", "lint")
    session.run("uv", "pip", "install", "safety", "pip-audit")
    session.run("uv", "run", "adt", "audit")


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.install("uv")
    session.run("uv", "sync", "--inexact")
    session.run("uv", "run", "pytest", "--tb=short")
