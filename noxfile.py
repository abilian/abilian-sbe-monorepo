import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.install("uv")
    session.run("uv", "sync", "--inexact")
    session.run("uv", "pip", "check")
    session.run("make", "lint", external=True)


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.install("uv")
    session.run("uv", "sync", "--inexact")
    session.run("pytest", "--tb=short")
