import os
import pandas as pd
import time

from contention_synthesis import Sledge, Bubble
import reporter
import constants
from workload import Workload

REPORTER_CORES = "0"
RESULTS_PATH = "test_results"

DIAL_START_MB = 0
DIAL_END_MB = 112
DIAL_STEP_MB = 4

def _get_sensitivity_data(workload_name: str) -> dict[int, float]:
    res = {}
    workload_file = workload_name.replace(".", "_")
    path = f"{RESULTS_PATH}/sensitivity/{workload_file}_data.csv"
    if not os.path.exists(path):
        return res
    with open(path, "r+") as f:
        next(f)
        for line in f:
            dial, perf = line.split(" ")
            res[int(dial)] = float(perf)
    return res


def _save_sensitivity_data(workload_name: str, sensitivity: dict[int, float]):
    benchmark_file = workload_name.replace(".", "_")
    with open(f"{RESULTS_PATH}/sensitivity/{benchmark_file}_data.csv", "w+") as f:
        f.write("footprint_mb perf\n")
        for k, v in sensitivity.items():
            f.write(f"{k} {v}\n")


def _profile_sensitivity(workload: Workload) -> str:
    sensitivity = _get_sensitivity_data(workload.name)
    for size_mb in range(DIAL_START_MB, DIAL_END_MB + DIAL_STEP_MB, DIAL_STEP_MB):
        if size_mb in sensitivity:
            continue
        sensitivity[size_mb] = _profile_sensitivity_dial(workload, size_mb)
        _save_sensitivity_data(workload.name, sensitivity)

def _profile_sensitivity_dial(workload: Workload, size_mb: int) -> float:
    if size_mb == 0:
        print("Profiling in isolation")
        return workload.run_once(constants.WORKLOAD_UNDER_PROFILING_CORES)
    bubble = Bubble(size_mb)
    bubble.run()
    try:
        return workload.run_once(constants.WORKLOAD_UNDER_PROFILING_CORES)
    finally:
        bubble.stop()

def _profile_contentiousness(workload: Workload):
        workload.run(constants.WORKLOAD_IN_BACKGROUND_CORES)
        try:
            time.sleep(20)
            return reporter.run_reporter(REPORTER_CORES)
        finally:
            workload.stop()

def _save_contentiousness_data(data: dict[str, dict[str,str]]):
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv(f"{RESULTS_PATH}/contentiousness.csv", sep=" ")

def profile_workloads(workloads: list[Workload]) -> None:
    contentiousness = {}
    for workload in workloads:
        _profile_sensitivity(workload)
    for workload in workloads:
        contentiousness[workload.name] = _profile_contentiousness(workload)
    _save_contentiousness_data(contentiousness)
