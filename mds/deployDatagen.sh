#!/bin/sh

docker pull ghcr.io/bruno-uva/datagen:latest

docker rm -f datagen

taskset -c 1 docker run -d --name=datagen --network my-net -p 9605:9605 ghcr.io/bruno-uva/datagen:latest