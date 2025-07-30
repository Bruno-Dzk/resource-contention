podman rm -f valkey-server
taskset -c 5 podman run -d -p 6379:6379 --network=my-net --name=valkey-server server
