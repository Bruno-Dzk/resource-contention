import subprocess
import os
import pandas as pd
import time
from collections import defaultdict

# INTRATE = [
#     "500.perlbench_r",
#     "502.gcc_r",
#     "505.mcf_r",
#     "520.omnetpp_r",
#     "523.xalancbmk_r",
#     "525.x264_r",
#     "531.deepsjeng_r",
#     "541.leela_r",
#     "548.exchange2_r",
#     "557.xz_r",
# ]

INTSPEED = [
    "600.perlbench_s",
    "602.gcc_s",
    "605.mcf_s",
    "620.omnetpp_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "631.deepsjeng_s",
    "641.leela_s",
    "648.exchange2_s",
    "657.xz_s",
]

FPSPEED = [
    "603.bwaves_s",
    "607.cactuBSSN_s",
    "619.lbm_s",
    # "621.wrf_s",
    "627.cam4_s",
    "628.pop2_s",
    "638.imagick_s",
    "644.nab_s",
    "649.fotonik3d_s",
    "654.roms_s",
]

SPEC_UNDER_PROFILING_CORES = "0-3"
SPEC_IN_BACKGROUND_CORES = "4-7"
SPEC_SIZE = "test"
SLEDGE_CORES = "4-7"
REPORTER_CORES = "0"
REPETITIONS = 10

ITERATIONS = 30
STEP_MB = 1
SLEDGE_ELEM_SIZE = 8


def profile_with_sledge(benchmark_name: str) -> str:
    data = defaultdict(dict)
    for i in range(ITERATIONS):
        size_sledge = i * STEP_MB * 1_000_000 // SLEDGE_ELEM_SIZE
        size_mb = i * STEP_MB
        sledge = None
        if i > 0:
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
            )
            sledge = subprocess.Popen(
                [
                    "sudo",
                    "nice",
                    "-n",
                    "-20",
                    "taskset",
                    "-c",
                    f"{SLEDGE_CORES}",
                    "./sledge",
                ],
                stdin=subprocess.DEVNULL,
            )
        else:
            print("Profiling in isolation")
        benchmark_time = run_benchmark(benchmark_name)
        data[size_mb]["runtime"] = benchmark_time
        if sledge:
            os.kill(sledge.pid, 9)

    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.reindex(sorted(df.columns), axis=1)
    print(df)

    csv_name = benchmark_name.replace('.', '_') + "_data.csv"
    df.to_csv(csv_name, sep=" ")


def get_output_filename(runcpu_output: str) -> str:
    for line in runcpu_output.splitlines():
        line = line.strip()
        if line.startswith("format: raw ->"):
            filename = line.split(" ")[3]
            if filename.endswith(".rsf"):
                return filename
    raise Exception("Output file not found")


def get_benchmark_time(output_file: str, benchmark_name: str):
    bench_format = benchmark_name.replace(".", "_")
    line_format = f"spec.cpu2017.results.{bench_format}.base.000.reported_time"
    with open(output_file, "r") as f:
        for line in f:
            if line.strip().startswith(line_format):
                return float(line.split(" ")[1])
        raise Exception("Benchmark reported time not found")
    
def run_background_benchmark(name: str) -> subprocess.Popen:
    print(f"Running {name} in background")
    return subprocess.Popen(
        [
            "sudo",
            "nice",
            "-n",
            "-20",
            "taskset",
            "-c",
            f"{SPEC_UNDER_PROFILING_CORES}",
            "/home/bruno/cpu2017/bin/runcpu",
            "--iterations=10000",
            "--config=try1",
            "--tuning=base",
            f"--size={SPEC_SIZE}",
            name,
        ],
        stdin=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )

def run_benchmark(name: str) -> float:
    print(f"Running benchmark {name}")
    proc = subprocess.run(
        [
            "sudo",
            "nice",
            "-n",
            "-20",
            "taskset",
            "-c",
            f"{SPEC_UNDER_PROFILING_CORES}",
            "/home/bruno/cpu2017/bin/runcpu",
            "--config=try1",
            "--tuning=base",
            f"--size={SPEC_SIZE}",
            name,
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
    )
    print("Started process")
    try:
        proc.check_returncode()
        output = proc.stdout.decode("utf-8")
        output_filename = get_output_filename(output)
        return get_benchmark_time(output_filename, name)

    except subprocess.CalledProcessError:
        errors = proc.stderr.decode("utf-8")
        print(errors)
        raise Exception
    
def run_reporter() -> float:
    print("Profiling with the reporter")
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
    res = {}
    for line in output.splitlines():
            if "median" in line:
                print(line.strip())
                line = line.split()
                res[line[0]] = float(line[1])
    return sum(res.values()) / len(res)

def get_contentiousness():
    data = {}
    for name in FPSPEED:
        proc = run_background_benchmark(name)
        time.sleep(20)
        data[name] = run_reporter()
        os.kill(proc.pid, 9)

    print(data)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_csv("results/contentiousness.csv", sep=" ")

def main() -> None:
    get_contentiousness()

if __name__ == "__main__":
    main()
