microk8s kubectl delete secret ghcr-pull-secret

microk8s kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=https://ghcr.io \
  --docker-username=$1 \
  --docker-password=$2 \
  --docker-email=$3