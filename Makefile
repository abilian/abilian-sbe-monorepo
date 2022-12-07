.PHONY: test unit full-test pep8 clean setup

PKG=extranet

default: test lint
all: default


#
# Deployment
#
deploy: push  ## Deploy to production
	./script/deploy

push: clean  ## Push code to production
	rsync -e ssh -avz \
		--exclude node_modules --exclude instance \
		--exclude .tox --exclude .idea --exclude .git \
		--exclude .venv --exclude .vscode \
		./ cnll@trunks:/home/cnll/extranet/src/


#
# testing
#
test:  ## Run tests
	# poetry run pytest --ff -x -n auto
	poetry run pytest --ff -x

test-with-coverage:
	poetry run pytest --durations=10			\
		--cov $(PKG)			\
		--cov-config coverage.rc	\
	  	--cov-report term-missing

test-with-validator:
	VALIDATOR_URL=http://html5.validator.nu/ poetry run pytest

test-long:
	RUN_SLOW_TESTS=True pytest -x

test-assets:
	@(if poetry run flask assets -v --parse-templates build 2>&1 \
	   | grep --silent "Failed, error was: ExternalTool: subprocess returned a non-success result code"; \
	then echo "Failed"; exit 1; \
	else echo "Success"; exit 0; \
	fi)

#
# Linting
#
.PHONY: check
check: lint  ## Statically check code

.PHONY: lint
lint: lint-py

.PHONY: lint-py
# lint-py: lint-flake8 lint-mypy
lint-py: lint-ruff lint-flake8

.PHONY: lint-flake8
lint-flake8:
	poetry run flake8 src tests

.PHONY: lint-ruff
lint-ruff:
	poetry run ruff *.py src tests

.PHONY: lint-mypy
lint-mypy:
	poetry run mypy --show-error-codes src tests


.PHONY: format
format: 
	poetry run black src tests *.py
	poetry run isort src tests *.py

#
# Everything else
#
.PHONY: run
run:  ## Run dev server
	honcho start


.PHONY:
run-ssl: run-ssl
	gunicorn -w1 --certfile=ssl/server.crt --keyfile=ssl/server.key --timeout 300 \
		--bind "0.0.0.0:5443" --pid run/gunicorn.pid wsgi:app

.PHONY: clean
clean:  ## Clean up directory
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
tidy: clean  ## Make super-clean
	rm -rf .tox

.PHONY:
update-pot: update-pot
	python setup.py extract_messages update_catalog compile_catalog


.PHONY: install
install:  ## Install dependencies
	@echo "--> Installing / updating python dependencies for development"
	pip install -qU pip setuptools wheel
	pip uninstall -y abilian-core abilian-sbe
	poetry install
	@echo "--> Activating pre-commit hook"
	pre-commit install
	yarn


.PHONY: update-deps
update-deps:  ## Update dependencies
	pip install -qU pip setuptools wheel
	poetry update
	poetry export -o requirements.txt --without-hashes


.PHONY: help
help: Makefile
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' \
		| sed -e 's/\[32m##/[33m/'
