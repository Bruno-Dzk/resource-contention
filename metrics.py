import requests

PROM_URL = "http://localhost:30987/api/v1/query"

def query_latency(metric_name: str) -> float:
    params = {
        "query": f"sum(rate({metric_name}[1m])) by (le)"
    }

    resp = requests.get(PROM_URL, params=params)
    resp.raise_for_status()   # raises if the request failed
    res = resp.json()['data']['result']
    if len(res) != 1:
        raise Exception("Result too big, should be of size 1")
    return res[0]['value'][1]