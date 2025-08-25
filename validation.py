import json
import spec
import os
import random
import csv
import time
from typing import Union
from collections import namedtuple

SPEC_SIZE = "train"

Prediction = namedtuple("Prediction", ("name1", "name2", "expected1", "expected2"))
ValidatedPrediction = namedtuple(
    "ValidatedPrediction", Prediction._fields + ("actual1", "actual2")
)


def get_key(prediction: Union[Prediction, ValidatedPrediction]) -> str:
    return f"{prediction.name1} + {prediction.name2}"


def read_predictions() -> list[Prediction]:
    with open("results/predictions.json", "r") as f:
        data = json.load(f)["predictions"]
        return [
            Prediction(p[0]["name"], p[1]["name"], p[0]["perf"], p[1]["perf"])
            for p in data
        ]


def profile_pair(primary: str, competitor: str) -> float:
    print(f"Starting profiling for pair ({primary}, {competitor})")
    isolated_perf = spec.run_benchmark(primary, "0-3", SPEC_SIZE)
    print(isolated_perf)
    competitor_proc = spec.run_background_benchmark(competitor, "4-7", SPEC_SIZE)
    time.sleep(20)
    try:
        perf = spec.run_benchmark(primary, "0-3", SPEC_SIZE)
        print(perf)
        return isolated_perf / perf
    finally:
        spec.stop_benchmark(competitor_proc)


def read_snapshot() -> dict[str, ValidatedPrediction]:
    with open(VALIDATION_FILE, "r+") as f:
        data = {}
        reader = csv.DictReader(f, delimiter=" ")
        for row in reader:
            vp = ValidatedPrediction(**row)
            data[get_key(vp)] = vp
        return data


def validate_prediction(prediction: Prediction):
    actual1 = profile_pair(prediction.name1, prediction.name2)
    actual2 = profile_pair(prediction.name2, prediction.name1)
    return ValidatedPrediction(actual1=actual1, actual2=actual2, *prediction)


VALIDATION_FILE = "results/validated.csv"


def writerow_and_sync(f, writer, row):
    writer.writerow(row)
    f.flush()  # flush Python buffers to OS
    os.fsync(f.fileno())  # force OS to write to disk


def main():
    snapshot = read_snapshot()
    # predictions = read_predictions()
    predictions = [Prediction(name1="628.pop2_s", name2="654.roms_s", expected1=0.0, expected2=0.0)]
    # predictions = random.sample(predictions, 30)
    # res = []
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
            row = validate_prediction(p)
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
    # print(read_validation())
    main()
    # update()
    # fx()
