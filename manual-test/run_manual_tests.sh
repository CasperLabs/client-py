#!/usr/bin/env bash

echo "Running CasperLabs builds..."
./build_contracts.sh || exit

echo "Standing up network..."
./standup.sh || exit

echo "Running Tests..."
pushd .. || exit
pipenv --rm
pipenv sync
pipenv run python setup.py develop
pipenv run pytest manual-test/tests
popd || exit

echo "Tearing down..."
./teardown.sh
