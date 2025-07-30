curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=sum(rate(req_duration_micros_bucket[1m])) by (le)'
  # --data-urlencode 'query=histogram_quantile(0.5, sum(rate(req_duration_micros_bucket[1m])) by (le))'