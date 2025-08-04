import subprocess
import os
import time
import pandas as pd
import requests
from collections import defaultdict

SLEDGE_ENABLED = True
SLEDGE_CORES = "1-4"
K6_CORES = "0"
START = 15
END = 31
STEP_MB = 1
SLEDGE_ELEM_SIZE = 8
PROFILE_TIME = 200 #60
QUERY_WINDOW = '180' #'40'

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
            ["sudo", "nice", "-n", "-20", "taskset", "-c", K6_CORES, "k6", "run", "constant-rate.js"],
            stdin=subprocess.DEVNULL,
            # stdout=subprocess.DEVNULL,
            stderr=open("k6-errors.log", "w"),
        )
        run_experiment()
    except Exception as e:
        print(e)
    finally:
        os.kill(k6.pid, 9)

def compile_sledge(size: int):
    subprocess.run(
            [
                "gcc",
                "-O2",
                "-fopenmp",
                f"-DLBM_SIZE={size}",
                "sledge.c",
                "-o",
                "sledge",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=open("sledge-errors.log", "w"),
        )

def profile_with_sledge():
    sledge_data = defaultdict(dict)
    for i in range(START, END):
        sledge_size = i * STEP_MB * 1_000_000 // SLEDGE_ELEM_SIZE
        compile_sledge(sledge_size)

        size_mb = i * STEP_MB
        print(f"Running sledge with footprint size {size_mb} MB")
        sledge = subprocess.Popen(
            ["sudo", "nice", "-n", "-20", "taskset", "-c", f"{SLEDGE_CORES}", "./sledge"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=open("sledge-errors.log", "w"),
        )
        try:
            sledge_data[size_mb] = profile_valkey()
        finally:
            os.kill(sledge.pid, 9)
    return sledge_data


def profile_valkey() -> dict:
    time.sleep(PROFILE_TIME)
    print(query_prometheus(f"rate(req_duration_micros_count[{QUERY_WINDOW}])"))
    return query_prometheus(
        f"histogram_quantile(0.5, sum(rate(req_duration_micros_bucket[{QUERY_WINDOW}])) by (le))"
    )

def run_experiment():
    print("Profiling in isolation")
    data = {}
    isolation_data = profile_valkey()
    data[0] = isolation_data
    
    if SLEDGE_ENABLED:
        print("Profiling with sledge")
        sledge_data = profile_with_sledge()
        data.update(sledge_data)
    
    df = pd.DataFrame.from_dict(data, orient="index")
    # df = df.reindex(sorted(df.columns), axis=1)
    print(df)

    df.to_csv("data.csv", sep=" ")
    return df

if __name__ == "__main__":
    main()


# OK  0 1 2 3 4 5 6 7
# DNS