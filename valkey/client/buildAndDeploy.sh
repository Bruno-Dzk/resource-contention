#!/bin/bash

VERSION=0.0.1

set -o pipefail
set -e

podman build . -t ci.tno.nl:4567/techflex/techflex-delivery/bruno-valkey:$VERSION
podman push ci.tno.nl:4567/techflex/techflex-delivery/bruno-valkey:$VERSION
kubectl delete -f valkey-client.yaml
kubectl apply -f valkey-client.yaml
