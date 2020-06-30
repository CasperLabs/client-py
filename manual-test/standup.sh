#!/usr/bin/env bash

docker pull casperlabs/execution-engine:dev
docker pull casperlabs/node:dev
docker pull casperlabs/key-generator:dev

export CL_VERSION=dev

# Stand up highway network
cd ../../CasperLabs/hack/docker || exit
make .casperlabs
make node-0/up
make node-1/up
make node-2/up

# Sleep until network starts.
while ! docker logs node-0 | grep "Executing action=StartRound(" ; do echo "Waiting for network startup.  Sleeping..."; sleep 10; done

echo "Network ready."
