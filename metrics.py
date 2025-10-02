import requests

PROM_URL = "http://145.100.131.48:30987/api/v1/query"

def query_latency(metric_name: str, profiling_time_s: int) -> float:

    params = {
        "query": f"histogram_quantile(0.5, sum(rate({metric_name}[{profiling_time_s}s])) by (le))"
    }

    resp = requests.get(PROM_URL, params=params)
    resp.raise_for_status()   # raises if the request failed
    res = resp.json()['data']['result']
    if len(res) != 1:
        raise Exception("Result is of wrong size, should be of size 1")
    return float(res[0]['value'][1])