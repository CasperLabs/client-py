#!/usr/bin/env bash


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Builds needed contracts from CasperLabs execution-engine to run network tests.
if [[ -z "$DRONE_BUILD_NUMBER" ]]; then
  # not inside CI, so we are not running in docker.
  docker run --rm -v $DIR/wasm:/wasm -v /tmp:/tmp \
         casperlabs/buildenv:latest \
         /bin/bash -c "$(cat $DIR/internal_build_script)"
else
  # inside CI, so we are running in buildenv docker
#  docker run --rm -v $DIR/wasm:/wasm -v /tmp:/tmp \
#         -v /var/run/docker.sock:/var/run/docker.sock \
#         casperlabs/buildenv:latest \
#         /bin/bash -c "$(cat $DIR/internal_build_script)"
  cd /tmp || exit 1
  git clone --depth 1 https://github.com/CasperLabs/CasperLabs

  cd /tmp/CasperLabs/execution-engine || exit 1
  cargo build --package faucet --target wasm32-unknown-unknown --release
  cargo build --package do-nothing --target wasm32-unknown-unknown --release
  cargo build --package test-payment-stored --target wasm32-unknown-unknown --release
  cargo build --package transfer-to-account-u512-stored --target wasm32-unknown-unknown --release

  cp target/wasm32-unknown-unknown/release/*.wasm "$DIR/wasm"
  cd /
  rm -rf /tmp/CasperLabs
fi
