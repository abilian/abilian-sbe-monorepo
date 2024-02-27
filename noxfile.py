import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12"]

nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("ruff", "flake8", "pyanalyze", "deptry", "mypy", "black", "isort")
    session.run("pip", "check")
    session.run("make", "lint", external=True)


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("html5lib", "pytest", "pytest-flask", "hyperlink")
    session.run("pip", "check")
    session.run("pytest", "--tb=short")
