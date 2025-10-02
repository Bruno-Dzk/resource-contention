import json
import os
import csv
import time
from typing import Union, List
from collections import namedtuple
import constants
from workload import Workload

Prediction = namedtuple("Prediction", ("name1", "name2", "expected1", "expected2"))
ValidatedPrediction = namedtuple(
    "ValidatedPrediction", Prediction._fields + ("actual1", "actual2")
)

def get_key(prediction: Union[Prediction, ValidatedPrediction]) -> str:
    return f"{prediction.name1} + {prediction.name2}"


def read_predictions() -> list[Prediction]:
    with open(f"{constants.RESULTS_DIR}/predictions.json", "r") as f:
        data = json.load(f)["predictions"]
        return [
            Prediction(p[0]["name"], p[1]["name"], p[0]["perf"], p[1]["perf"])
            for p in data
        ]

def profile_pair(primary: Workload, competitor: Workload) -> float:
    print(f"Starting profiling for pair ({primary.name}, {competitor.name})")
    isolated_perf = primary.profile(constants.WORKLOAD_UNDER_PROFILING_CORES)
    print(isolated_perf)
    competitor.run_in_background(constants.WORKLOAD_IN_BACKGROUND_CORES)
    time.sleep(20)
    try:
        perf = primary.profile(constants.WORKLOAD_UNDER_PROFILING_CORES)
        print(perf)
        return isolated_perf / perf
    finally:
        competitor.stop()

def read_snapshot() -> dict[str, ValidatedPrediction]:
    if not os.path.exists(VALIDATION_FILE):
        return {}
    with open(VALIDATION_FILE, "r") as f:
        data = {}
        reader = csv.DictReader(f, delimiter=" ")
        for row in reader:
            vp = ValidatedPrediction(**row)
            data[get_key(vp)] = vp
        return data


def validate_prediction(prediction: Prediction, workload_map: dict[str, Workload]):
    workload1 = workload_map[prediction.name1]
    workload2 = workload_map[prediction.name2]
    actual1 = profile_pair(workload1, workload2)
    actual2 = profile_pair(workload2, workload1)
    return ValidatedPrediction(actual1=actual1, actual2=actual2, *prediction)


VALIDATION_FILE = f"{constants.RESULTS_DIR}/validated.csv"


def writerow_and_sync(f, writer, row):
    writer.writerow(row)
    f.flush()  # flush Python buffers to OS
    os.fsync(f.fileno())  # force OS to write to disk


def validate_predictions(workloads: List[Workload]):
    snapshot = read_snapshot()
    predictions = read_predictions()
    workload_map = {w.name: w for w in workloads}
    with open(VALIDATION_FILE, "a+") as f:
        f.seek(0)
        is_empty = f.read(1) == ""

        writer = csv.writer(f, delimiter=" ")
        if is_empty:
            writer.writerow(ValidatedPrediction._fields)

        f.seek(0, os.SEEK_END)

        for p in predictions:
            key = get_key(p)
            if key in snapshot:
                continue
            row = validate_prediction(p, workload_map)
            writerow_and_sync(f, writer, row)


def update():
    vps = read_snapshot()
    predictions = read_predictions()

    updated = []
    for p in predictions:
        key = get_key(p)
        if key not in vps:
            continue
        new_pred = ValidatedPrediction(
            name1=vps[key].name1,
            name2=vps[key].name2,
            actual1=vps[key].actual1,
            actual2=vps[key].actual2,
            expected1=p.expected1,
            expected2=p.expected2,
        )
        updated.append(new_pred)

    with open(VALIDATION_FILE, "w") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerow(ValidatedPrediction._fields)
        for vp in updated:
            writer.writerow(vp)


# def fx():
#     with open("results/validated.json", "r") as f:
#         data = json.load(f)

#     with open("results/validated.csv", "w+") as f:
#         f.write("name1 name2 expected1 expected2 actual1 actual2\n")
#         for p in data:
#             f.write(f"{p[0]['name']} {p[1]['name']} {p[0]['perf']} {p[1]['perf']} {p[0]['actual']} {p[1]['actual']}\n")

if __name__ == "__main__":
    # main()
    # validate_predictions()
    # update()
    pass