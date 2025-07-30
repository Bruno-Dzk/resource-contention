#!/bin/bash

VERSION=0.0.1

podman build . -t ci.tno.nl:4567/techflex/techflex-delivery/bruno-valkey-server:$VERSION
podman push ci.tno.nl:4567/techflex/techflex-delivery/bruno-valkey-server:$VERSION
kubectl delete -f valkey-server.yaml
kubectl apply -f valkey-server.yaml