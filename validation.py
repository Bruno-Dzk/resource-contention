import json
import subprocess
import spec
from collections import namedtuple

SPEC_SIZE = 'test'

def read_predictions() -> list[list[dict]]:
    with open("results/predictions.json", "r") as f:
        return json.load(f)['predictions']
    
def profile_pair(primary: str, competitor: str) -> float:
    isolated_perf = spec.run_benchmark(primary, '0-3', SPEC_SIZE)
    competitor_proc = spec.run_background_benchmark(competitor, '4-7', SPEC_SIZE)
    try:
        perf = spec.run_benchmark(primary, '0-3', SPEC_SIZE)
        return isolated_perf / perf
    finally:
        spec.stop_benchmark(competitor_proc)

def main():
    predictions = read_predictions()
    res = []
    for prediction in predictions:
        print(prediction)
        if len(prediction) != 2:
            raise Exception("Only pairwise predictions are supported")
        actual1 = profile_pair(prediction[0]['name'], prediction[1]['name'])
        actual2 = profile_pair(prediction[1]['name'], prediction[0]['name'])
        validated_prediction = [
            dict({'actual': actual1}, **prediction[0]),
            dict({'actual': actual2}, **prediction[1])
        ]
        res.append(validated_prediction)

    
    with open("results/validated.json", 'w+') as f:
        json.dump(res, f)

if __name__ == "__main__":
    main()
