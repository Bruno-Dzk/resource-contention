docker rm -f prometheus

docker run -d \
  --name prometheus \
  -p 9090:9090 \
  --network=my-net \
  -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  prom/prometheus:latest