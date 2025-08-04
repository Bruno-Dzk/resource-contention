set -oe pipefail

docker build client -t client
docker build server -t server