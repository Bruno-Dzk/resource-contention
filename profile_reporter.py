import pandas as pd
import time
from collections import defaultdict

import reporter
from contention_synthesis import Bubble, Sledge

REPORTER_CORES = "0"
REPETITIONS = 100

DIAL_START = 0
DIAL_STEP_MB = 2
DIAL_END = 112

def main():
    data = defaultdict(dict)
    for i in range(DIAL_START, DIAL_END + DIAL_STEP_MB, DIAL_STEP_MB):
        size_mb = i * DIAL_STEP_MB
        if size_mb == 0:
            print("Profiling in isolation")
            data[size_mb] = reporter.run_reporter(REPORTER_CORES)
            continue
        
        bubble = Bubble(size_mb)
        bubble.run()
        time.sleep(10)
        data[size_mb] = reporter.run_reporter(REPORTER_CORES)
        print(data)
        if bubble:
            bubble.stop()

    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.reindex(sorted(df.columns), axis=1)
    print(df)

    df.to_csv("data.csv", sep=" ")

if __name__ == "__main__":
    main()
