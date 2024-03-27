.PHONY: test unit full-test pep8 clean setup

default: test lint
all: default


#
# testing
#

## Run tests
test:
	# pytest -n auto tests
	pytest tests

test-with-coverage:
	pytest tests \
		--cov extranet --cov abilian \
	  	--cov-report term-missing

test-with-validator:
	VALIDATOR_URL=http://html5.validator.nu/ pytest tests

test-long:
	RUN_SLOW_TESTS=True pytest -x tests

test-assets:
	@(if flask assets -v --parse-templates build 2>&1 \
	   | grep --silent "Failed, error was: ExternalTool: subprocess returned a non-success result code"; \
	then echo "Failed"; exit 1; \
	else echo "Success"; exit 0; \
	fi)


#
# Linting
#
.PHONY: check
## Statically check code, dependencies, etc.
check: lint

.PHONY: lint
lint: lint-py

.PHONY: lint-py
lint-py:
	ruff check src tests
	flake8 src tests
	deptry src
	python -m pyanalyze --config-file pyproject.toml
	# mypy --show-error-codes src tests
	# pyright src tests

.PHONY: lint-mypy
lint-mypy:
	mypy --show-error-codes src tests

.PHONY: lint-pyright
lint-pyright:
	pyright src tests


.PHONY: format
format:
	black src tests *.py
	isort src tests *.py


#
# Everything else
#
.PHONY: run
## Run dev server
run:
	honcho -f Procfile.dev start

.PHONY:
run-ssl: run-ssl
	gunicorn -w1 --certfile=ssl/server.crt --keyfile=ssl/server.key --timeout 300 \
		--bind "0.0.0.0:5443" --pid run/gunicorn.pid wsgi:app

.PHONY: clean
## Clean up directory
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -depth -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf build dist tmp __pycache__
	rm -rf pip-wheel-metadata
	rm -rf *.egg-info *.egg .coverage .eggs
	rm -rf doc/_build htmlcov
	rm -rf instance/cache instance/webassets
	rm -rf src/instance/cache src/instance/webassets
	rm -rf .mypy_cache .pytest_cache

.PHONY: tidy
## Make super-clean
tidy: clean
	rm -rf .tox .nox

.PHONY:
update-pot: update-pot
	python setup.py extract_messages update_catalog compile_catalog


.PHONY: install
## Install dependencies
install:
	@echo "--> Installing / updating python dependencies for development"
	@echo "Make sure that you have Poetry installed (https://python-poetry.org/)"
	poetry install
	@echo "--> Activating pre-commit hook"
	pre-commit install
	@echo "Remember to run `poetry shell` to activate the virtualenv"
	yarn


.PHONY: update-deps
update-deps:  ## Update dependencies
	pip install -qU pip setuptools wheel
	poetry update
	poetry export -o requirements.txt --without-hashes


.PHONY: help
help:
	adt help-make


.PHONY: help
## Publish to PyPI
publish: clean
	git push --tags
	poetry build
	twine upload dist/*
