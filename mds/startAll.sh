#!/bin/bash

set -oe pipefail

docker-compose down -v
docker container rm -f etcd datagen datafwd || 1
docker-compose pull  && docker-compose up -d