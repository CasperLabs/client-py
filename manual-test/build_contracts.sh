#!/usr/bin/env bash

# build contracts to use
pushd ../../CasperLabs/execution-engine || exit
cargo build --package faucet --target wasm32-unknown-unknown --release
popd

