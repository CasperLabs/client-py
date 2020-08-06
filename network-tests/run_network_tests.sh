#!/usr/bin/env bash
# We are buffering output and suppressing all but tests if they exit cleanly.

output_and_exit() {
  echo "$output"
  exit 1
}


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

trap "./teardown.sh" EXIT

cd "$DIR" || exit 1
if [ ! "$(ls -A wasm)" ]; then
  echo "Building required WASM contracts..."
  output=$(./build_contracts_in_buildenv.sh 2>&1) || output_and_exit
else
  echo "WASM found in network-tests/wasm and assumed to be current."
  echo "Delete all .wasm files in this directory to trigger local rebuild,"
  echo "or manually run build_contracts_in_buildenv.sh."
fi


echo "Standing up network..."
output=$(./standup.sh 2>&1) || output_and_exit

echo "Running Tests..."
pushd .. || exit 1
pipenv --rm
pipenv sync
pipenv run python setup.py develop
pipenv run pytest network-tests/tests
popd || exit 1

echo "Tearing down..."
output=$(./teardown.sh 2>&1) || output_and_exit

echo "Complete"
