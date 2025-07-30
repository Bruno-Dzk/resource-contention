podman rm -f valkey-client
taskset -c 6-7 podman run -d -p 3003:3003 --network=my-net --name=valkey-client client