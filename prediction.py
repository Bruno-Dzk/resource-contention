import itertools
import json

import constants

def get_contentiousness() -> dict[str, int]:
    scores = {}
    with open(f"{constants.RESULTS_DIR}/contentiousness_scores.csv", "r") as f:
        for line in f:
            bench, score = line.split(" ")
            scores[bench] = int(score)
    return scores


def get_sensitivity(benchmark: str) -> dict[int, float]:
    res = {}
    benchmark_file = benchmark.replace(".", "_")
    with open(f"{constants.RESULTS_DIR}/sensitivity/{benchmark_file}_data.csv", "r") as f:
        next(f)
        for line in f:
            dial, perf = line.split(" ")
            res[int(dial)] = float(perf)
    return res


def pairwise_prediction(
    benchmark1: str,
    benchmark2: str,
    scores: dict[str, int],
    sensitivity: dict[str, dict[int, float]],
) -> tuple[float, float]:
    perf1 = sensitivity[benchmark1][scores[benchmark2]]
    perf2 = sensitivity[benchmark2][scores[benchmark1]]
    # Divide isolation b prediction to normalize
    return (
        {"name": benchmark1, "perf": sensitivity[benchmark1][0] / perf1},
        {"name": benchmark2, "perf": sensitivity[benchmark2][0] / perf2},
    )


def calculate_predictions():
    scores = get_contentiousness()
    benchmarks = list(scores.keys())
    pairs = list(itertools.combinations(benchmarks, 2))

    sensitivity = {b: get_sensitivity(b) for b in benchmarks}

    res = []
    for b1, b2 in pairs:
        pred1, pred2 = pairwise_prediction(b1, b2, scores, sensitivity)
        res.append([pred1, pred2])

    json_data = json.dumps({"predictions": res})

    with open(f"{constants.RESULTS_DIR}/predictions.json", "w") as f:
        f.write(json_data)


if __name__ == "__main__":
    calculate_predictions()
