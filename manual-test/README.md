# Manual Testing

This directory holds tests of the client into the network
with `CasperLabs/hack/docker` and assumes that `client-py` repo is at the same directory level as the 
`CasperLabs` repo.  

 - Run `./build_contracts.sh` to build any wasm used.
 - Run `./standup.sh` to bring up 3 node network. 
   This pulls images from dockerhub tagged with `dev` by default. 
   If you wish to use other tags, export CL_VERSION with the tag to be used.
 - Run python tests.
 - Run `./teardown.sh` to bring down network when finished.

The full test cycle can be run with `run_manual_tests.sh`.  