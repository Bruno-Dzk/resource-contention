set -oe pipefail

curl -v -X POST localhost:3003/init
curl -v -X POST localhost:3004/init