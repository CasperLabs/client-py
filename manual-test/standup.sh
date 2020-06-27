#!/usr/bin/env bash

# Stand up highway network
cd ../../CasperLabs/hack/docker || exit
make .casperlabs
make node-0/up
make node-1/up
make node-2/up

