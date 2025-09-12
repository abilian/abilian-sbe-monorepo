# Changelog

All notable changes to this project will be documented in this file.

## [1.1.15] - 2025-09-12

### Bug Fixes
- Remove dependency on mmdb-writer and netaddr
- Fix mypy type checking issues

### Chore
- Update dependencies and SlapOS configuration files
- Extensive ruff configuration improvements and formatting
- Update requirements.txt and sync dependencies

### Refactor
- Add comprehensive type annotations
- Cast using strings instead of types
- Modernize code with dataclasses and improved patterns
- Move returns out of else clauses for cleaner code
- Use dataclasses and modernize code patterns

## [1.1.13] - 2024-11-04

### Bug Fixes
- Fix race conditions in task processing
- Update SlapOS configuration files
- Fix CLI commands and missing dependencies
- Fix typing issues and refactoring errors

### Features
- Add nixpacks support for deployment
- Add Nix support for development environment

### Documentation
- Add Architecture Decision Records (ADRs)
- Update roadmap and development documentation
- Add contribution guidelines and build badges
- Improve README and installation guides

### Chore
- Migrate from Poetry to UV package manager
- Remove ClamAV dependency
- Extensive dependency updates
- Improve CI/CD configuration
- Add REUSE compliance for licensing
- Remove unused modules and clean up imports

### Refactor
- Simplify application class with less inheritance
- Refactor services and app setup
- Extensive code modernization and cleanup
- Replace isort with ruff for import sorting
- Add comprehensive type annotations

## [1.1.12] - 2024-05-08

### Documentation
- Add governance documentation
- Update licensing information

### Chore
- Update dependencies
- Improve REUSE compliance

## [1.1.11] - 2024-05-06

### Features
- Add Nix support for development environment

### Chore
- Extensive dependency updates
- Protect secrets in configuration
- Code formatting improvements

## [1.1.10] - 2024-04-25

### Documentation
- Update TODO list

### Chore
- Add type annotations
- Multiple dependency updates

## [1.1.9] - 2024-04-04

### Chore
- Dependency updates

## [1.1.8] - 2024-04-04

### Bug Fixes
- Fix imports for SQLAlchemy 2.x compatibility

### Chore
- Update html2text dependency
- Modernize Flask-SQLAlchemy imports
- Code cleanup and dependency updates
- Silence ruff warnings and improve configuration

## [1.1.7] - 2024-03-27

### Chore
- Remove unused tailwind dependency

## [1.1.6] - 2024-03-27

### Bug Fixes
- Fix error on forum attachment uploads
- Fix "FolderishModel not mapped" test issue

### Refactor
- Remove unused code: BaseCriterion, TextSearchCriterion, TextCriterion, TagCriterion

### Chore
- Update dependencies and ruff configuration

## [1.1.2, 1.1.3, 1.1.4 and 1.1.5] - 2024-03-26

- Bugfix: fix live-search

## [1.1.2] - 2024-03-25

- Temp fix: deactivate live-search to fix issue on rich text editor

## [1.1.1] - 2024-03-25

- Cleanup "sysinfo" code.
- Cleanup imports
- Update PyPI metadata


## [1.1.0] - 2024-03-23

- Dropped support for Python < 3.10
- Upgrade many dependencies
- Switch from Celery to Dramatiq

## [1.0.5]

### Bug Fixes

- Adapt `_vocabularies()` function to `sqlalchemy` v1.3.24.
- Monkeypatch tests for `dramatiq` use (forum, wiki, communities, documents).
- If root user (user 0) not present, create it during initialization.
- Make sure only one LibreOffice process is running at any time to fix conversion failure (via locking).
- Better detection of `lessc`, permit to configure its path with `FLASK_LESS_BIN`.

### Continuous Integration

- Update pre-commit dependencies.
- Ensure `pip_audit` is updated in `tox.ini`.
- Update `adt` command in `tox.ini` (adt security-check -> adt audit).
- Remove `git-cliff`.

### Documentation

- Add `example_config` folder with step by step install procedure.
- Add Nua config example.
- Add SlapOS config example.

### Features

- Task scheduler crontab can be configured through `flask.config` (or `.env`).

### Refactor

- Update Python to version 3.12.
- Move logging system to `Loguru`.
- Complete removal of `Celery`, use now `Dramatiq` task manager.
- `Dramatiq` configured with: `flask-dramatiq`, `dramatiq-abort`, `apscheduler`.
- Add `honcho` dependency, provide a default `Procfile`.
- Provide a `.env` example (named `dot_env.example`).
- Provide an explicit `wsgi.py` file in extranet package.
- Permit flask configuration from environment, using `.from_prefixed_env()`.
- Update dependencies.

## [1.0.2] - 2023-10-04

### Bug Fixes

- Remove duplicate dependency.
- App.json was malformed.

### Documentation

- Update README (esp. install procedure).
- Add "npm install" step.
- Start using git-cliff.

### Refactor

- Simplify configuration management.

## [1.0.1] - 2023-06-06

### Bug Fixes

- Downgrade SQLAlchemy to 1.2.* to workaround some bugs.
- Use env variables for prod too.
- Workaround production bug.
- Celery config.
- Celery fixes.
- Celery debug
- Add missing dependency on toml.
- Remove debug instruction.
- Don't fail too hard when attachment is not available.
- Run all tests.
- Typing issue.
- Html.
- Revert tailwind experiment.
- Work under Python 3.11.
- Use new keyword for tox.

### Continuous Integration

- Add GH workflow config.
- Circleci config.
- Add missing safety module.
- Config (fix 'safety' target)
- Silence all flake8 warnings.
- Debug CI failure.
- Faster and cleaner tox config.
- Add safety check to default tox target.
- Don't use cache.
- Fix failure on Circle.
- Sourcehut config.
- Try using Alpine
- Alpine tweak.
- Tweak alpine and add ubuntu.
- Fix ubuntu build (?)
- Alpine fix
- Fix builds (?)
- Change task order.
- Another fix.
- Another fix.
- Update CircleCI and tox scripts.
- Don't run "safety" job for now.
- Fix tox config.
- Fix github action config.
- Another fix

### DevOps/Deployment

- Try to deploy on Heroku.
- Not need for setup.py
- Workaround platform issue.
- Remove debug code.

### Documentation

- Add a TODO.

### Features

- Add '-y' option to dropdb.
- Start dockerizing.

### Refactor

- Cleanup imports.
- Fix some typing issues.
- Cleanup / typing.
- Import the future (annotations)
- Remove unneeded injected arg.
- We don't need these injections.
- More deprecation updates.
- Upgrade celery and fix issues.
- Configuration + celery
- Simplify celery tasks.
- Modernize annotations (Python 3.8+)
- Simplify tests fixtures.
- Cleanup imports.
- Modernize (use `super()`).
- Rename "repository" service to "blob_store".
- Rename blob storage service + modernize tests.
- Rename class.
- Fix some warnings.
- Remove unneeded arguments.
- Add flask-tailwind files.
- Remove old IE support (was broken anyway)
- Remove deprecated macros.
- Use honcho.
- Drop python3.8 support and test against py3.11.
- Use contextlib.suppress.
- Simplify if statements.
- Use f-strings

### CI

- Ci lint build

### Misc

- Investigate failing test.

<!-- generated by git-cliff -->
