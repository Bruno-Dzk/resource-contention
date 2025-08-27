import subprocess

def run_reporter(cores: str, repetitions: int = 10) -> float:
    print("Profiling with the reporter")
    reporter = subprocess.run(
        [
            "sudo",
            "nice",
            "-n",
            "-19",
            "taskset",
            "-c",
            f"{cores}",
            "./reporter",
            "--benchmark_min_warmup_time=1",
            f"--benchmark_repetitions={repetitions}",
            "--benchmark_enable_random_interleaving=true",
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
