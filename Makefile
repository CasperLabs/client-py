.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-make  ## remove all make, build, test, coverage and Python artifacts

.make:
	mkdir .make

.make/pipenv: .make
	pipenv install --deploy
	touch .make/pipenv

clean-make:  ## remove make flags that short circuit steps.
	rm -rf .make

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: .make/pipenv ## check style with flake
	pipenv run flake8 casperlabs_client tests

test: .make/pipenv ## run tests quickly with the default Python
	pipenv run pytest tests

test-all: .make/pipenv ## run tests on every Python version with tox
	pipenv run tox

coverage-base: .make/pipenv
	pipenv run coverage run --source casperlabs_client -m pytest tests

coverage: coverage-base ## check code coverage quickly with the default Python
	pipenv run coverage report -m

coverage-html: coverage-base  ## check code coverage with html display
	pipenv run coverage html
	$(BROWSER) htmlcov/index.html

build: .make/pipenv clean-build ## builds source package
	pipenv run python setup.py sdist

develop: .make/pipenv ## install the package into pipenv for development
	pipenv run python setup.py develop

install: build  ## Install to local environment with pip
	pip install dist/casperlabs_client*

docker:  ## Build local docker image to casperlabs/client:latest
	docker build -t casperlabs/client:latest .

pre-commit:  ## Run the pre-commit scripts
	pipenv run pre-commit run

pre-commit-all:  ## Run the pre-commit scripts as if all files are staged
	pipenv run pre-commit run --all-files
