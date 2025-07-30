import subprocess
import os
import time
import pandas as pd
import requests
from collections import defaultdict

SLEDGE_ENABLED = False
SLEDGE_CORES = "1-4"
ITERATIONS = 4
STEP_MB = 1
SLEDGE_ELEM_SIZE = 8
PROFILE_TIME = 60
QUERY_WINDOW = '40'

def query_prometheus(
    query: str,
    host: str = "localhost",
    port: int = 9090,
    timeout: float = 5.0
) -> dict:
    url = f"http://{host}:{port}/api/v1/query"
    params = {
        "query": query
    }
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    print(response.json())
    val = data['data']['result'][0]['value'][1]
    return val

def main():
    try:
        k6 = subprocess.Popen(
            ["sudo", "nice", "-n", "-20", "taskset", "-c", "1", "k6", "run", "constant-rate.js"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=open("k6-errors.log", "w"),
        )
        profile_valkey()
    except Exception as e:
        print(e)
    finally:
        os.kill(k6.pid, 9)

def profile_valkey() -> pd.DataFrame:
    data = defaultdict(dict)
    for i in range(ITERATIONS):
        size_sledge = i * STEP_MB * 1_000_000 // SLEDGE_ELEM_SIZE
        size_mb = i * STEP_MB
        sledge = None
        
        if i > 0 and SLEDGE_ENABLED:
            print(f"Running sledge with footprint size {size_mb} MB")
            subprocess.run(
                [
                    "gcc",
                    "-O2",
                    "-fopenmp",
                    f"-DLBM_SIZE={size_sledge}",
                    "sledge.c",
                    "-o",
                    "sledge",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=open("sledge-errors.log", "w"),
            )
            sledge = subprocess.Popen(
                ["sudo", "nice", "-n", "-20", "taskset", "-c", f"{SLEDGE_CORES}", "./sledge"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=open("sledge-errors.log", "w"),
            )
        else:
            print("Profiling in isolation")

        time.sleep(PROFILE_TIME)
        latency = query_prometheus(
            f"histogram_quantile(0.5, sum(rate(req_duration_micros_bucket[{QUERY_WINDOW}])) by (le))"
        )
        query_prometheus(f"rate(req_duration_micros_count[{QUERY_WINDOW}])")

        data[size_mb] = latency
        
        if sledge:
            os.kill(sledge.pid, 9)

    
    df = pd.DataFrame.from_dict(data, orient="index")
    # df = df.reindex(sorted(df.columns), axis=1)
    print(df)

    df.to_csv("data.csv", sep=" ")
    return df

if __name__ == "__main__":
    main()


# OK  0 1 2 3 4 5 6 7
# DNS