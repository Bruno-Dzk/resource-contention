import subprocess
import os
import pandas as pd
import time
from collections import defaultdict
import spec
import constants

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
SPEC_SIZE = "train"  # "test"
SLEDGE_CORES = "4-7"
REPORTER_CORES = "0"
REPETITIONS = 10

ITERATIONS = 30
STEP_MB = 1
SLEDGE_ELEM_SIZE = 8


def run_sledge(size: int) -> subprocess.Popen:
    size_sledge = size * STEP_MB * 1_000_000 // SLEDGE_ELEM_SIZE
    print(f"Running sledge with footprint size {size_sledge}")
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
    return subprocess.Popen(
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


def get_sensitivity(benchmark: str) -> dict[int, float]:
    res = {}
    benchmark_file = benchmark.replace(".", "_")
    path = f"{constants.RESULTS_DIR}/sensitivity/{benchmark_file}_data.csv"
    if not os.path.exists(path):
        return res
    with open(path, "r+") as f:
        next(f)
        for line in f:
            dial, perf = line.split(" ")
            res[int(dial)] = float(perf)
    return res


def save_sensitivity(benchmark: str, sensitivity: dict[int, float]):
    benchmark_file = benchmark.replace(".", "_")
    with open(f"{constants.RESULTS_DIR}/sensitivity/{benchmark_file}_data.csv", "w+") as f:
        f.write("footprint_mb perf\n")
        for k, v in sensitivity.items():
            f.write(f"{k} {v}\n")


def profile_with_sledge(benchmark_name: str) -> str:
    sensitivity = get_sensitivity(benchmark_name)
    print(sensitivity)
    for i in range(ITERATIONS):
        size_mb = i * STEP_MB
        if size_mb in sensitivity:
            continue
        sledge = None
        if i > 0:
            sledge = run_sledge(i)
        else:
            print("Profiling in isolation")
        benchmark_time = run_benchmark(benchmark_name)
        sensitivity[size_mb] = benchmark_time
        if sledge:
            os.kill(sledge.pid, 9)
        save_sensitivity(benchmark_name, sensitivity)


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
    return {
        "avg": sum(res.values()) / len(res),
        "rand": res["rand_smash_median"],
        "stream": res["smash_median"],
    }


def get_contentiousness():
    data = {}
    for name in FPSPEED + INTSPEED:
        proc = spec.run_background_benchmark(name, "4-7", "train")
        time.sleep(20)
        data[name] = run_reporter()
        print(data[name])
        os.kill(proc.pid, 9)

    print(data)
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv("results/contentiousness.csv", sep=" ")


def main() -> None:
    for bench in FPSPEED + INTSPEED:
        profile_with_sledge(bench)
    # get_contentiousness()


if __name__ == "__main__":
    main()
