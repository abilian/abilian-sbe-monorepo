import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]

nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.run("poetry", "install", external=True)
    session.run("pip", "check")
    session.run("make", "lint", external=True)


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.run("poetry", "install", external=True)
    session.run("pip", "check")
    session.run("pytest", "--tb=short")
