microk8s kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=https://ghcr.io \
  --docker-username=bruno-uva@github.com \
  --docker-password=$CR_PAT \
  --docker-email=bruno.dzikowski@student.uva.nl