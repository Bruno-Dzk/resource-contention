podman rm -f valkey-server-clone
podman rm -f valkey-client-clone

taskset -c 2 podman run -d -p 9004:6379 --network=clone-net --name=valkey-server-clone server
sleep 120
taskset -c 3-4 podman run -d -p 3004:3003 --network=clone-net --name=valkey-client-clone client-clone