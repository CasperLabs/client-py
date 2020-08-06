# Network Testing

This directory holds tests of the client into a live network.

 - Run `./build_contracts_in_buildenv.sh` to build wasm using `casperlabs/buildenv:latest` docker image.
 - Run `./standup.sh` to bring up 1 node network.
   This pulls images from dockerhub tagged with `latest` by default.
   If you wish to use other tags, export CL_VERSION with the tag to be used.
 - Run python tests.
 - Run `./teardown.sh` to bring down network when finished.

The full test cycle can be run with `./run_network_tests.sh` or `make network-test` in root directory.
