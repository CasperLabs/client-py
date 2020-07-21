#!/usr/bin/env bash

TAG=${CL_VERSION:-"dev"}
docker pull casperlabs/execution-engine:"$TAG"
docker pull casperlabs/node:"$TAG"
docker pull casperlabs/key-generator:"$TAG"

export CL_VERSION="$TAG"

# Stand up highway network
cd ../../CasperLabs/hack/docker || exit
make .casperlabs
make node-0/up
make node-1/up
make node-2/up

# Sleep until network starts.
while ! docker logs node-0 | grep "Executing action=StartRound(" ; do echo "Waiting for network startup.  Sleeping..."; sleep 10; done

echo "Network ready."
