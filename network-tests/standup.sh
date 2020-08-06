#!/usr/bin/env bash

TAG=${CL_VERSION:-"latest"}
docker pull casperlabs/execution-engine:"$TAG"
docker pull casperlabs/node:"$TAG"
docker pull casperlabs/key-generator:"$TAG"

export CL_VERSION="$TAG"

# Stand up highway network
cd ../hack/docker || exit
make .casperlabs
make node-0/up

count=0

# Sleep until network starts.
while ! docker logs node-0 | grep "Executing action=StartRound("
do
  ((count=count+1))
  if [ $count -gt 12 ]; then
    echo "Network startup timeout.  Outputting docker logs."
    docker logs node-0
    exit 1
  fi

  echo "Waiting for network startup.  Sleeping...";
  sleep 10
done

echo "Network ready."
