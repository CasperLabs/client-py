#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}

# Remove and reinstall pipenv to validate Pipenv
pipenv --rm
pipenv sync
pipenv run python setup.py develop
pipenv run pytest tests