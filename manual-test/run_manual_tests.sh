#!/usr/bin/env bash

# We are buffering output and suppressing all but tests if they exit cleanly.

output_and_exit() {
  echo "$output"
  exit
}

echo "Running CasperLabs builds..."
output=$(./build_contracts.sh 2>&1) || output_and_exit

echo "Standing up network..."
output=$(./standup.sh 2>&1) || output_and_exit

echo "Running Tests..."
pushd .. || exit
pipenv --rm
pipenv sync
pipenv run python setup.py develop
pipenv run pytest manual-test/tests
popd || exit

echo "Tearing down..."
output=$(./teardown.sh 2>&1) || output_and_exit

echo "Complete"
