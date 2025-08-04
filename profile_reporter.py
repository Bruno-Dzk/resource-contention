import subprocess
import os
import time
import pandas as pd
from collections import defaultdict

SLEDGE_ENABLED = False
SLEDGE_CORES = "1-4"
REPORTER_CORES = "0"
REPETITIONS = 10
ITERATIONS = 3
STEP_MB = 1
SLEDGE_ELEM_SIZE = 8

if __name__ == "__main__":
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
                ]
            )
            sledge = subprocess.Popen(
                ["sudo", "nice", "-n", "-20", "taskset", "-c", f"{SLEDGE_CORES}", "./sledge"]
            )
        else:
            print("Profiling in isolation")
        reporter = subprocess.run(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                f"{REPORTER_CORES}",
                "./reporter",
                "--benchmark_min_warmup_time=1",
                f"--benchmark_repetitions={REPETITIONS}",
                "--benchmark_enable_random_interleaving=true",
                # "--benchmark_min_time=0.1",
            ],
            capture_output=True,
        )
        output = reporter.stdout.decode("utf-8")
        for line in output.splitlines():
            if "median" in line:
                print(line.strip())
                line = line.split()
                data[size_mb][line[0]] = line[1]
        if sledge:
            os.kill(sledge.pid, 9)

    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.reindex(sorted(df.columns), axis=1)
    print(df)

    df.to_csv("data.csv", sep=" ")


# 00000001
