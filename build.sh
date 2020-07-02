#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}

rm -rf dist/*

# Does same as sync, but aborts if Pipfile and Pipfile.lock are not in sync.
pipenv install --deploy
pipenv run python setup.py sdist
