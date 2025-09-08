import time

import reporter as rp
from contention_synthesis import Bubble
import constants

REPORTER_CORES = "0"
REPETITIONS = 100

DIAL_START = 0
DIAL_STEP_MB = 4
DIAL_END = 112

reporter = rp.AveragingReporter("reporters/reporter")


def profile_sensitivity(size_mb: int) -> float:
    if size_mb == 0:
        print("Profiling in isolation")
        return reporter.run(REPORTER_CORES)
    bubble = Bubble(size_mb)
    bubble.run()
    time.sleep(5)
    try:
        return reporter.run(REPORTER_CORES)
    finally:
        bubble.stop()


def profile_reporter():
    with open(f"{constants.RESULTS_DIR}/reporter_sensitivity.csv", "a+") as f:
        for size_mb in range(DIAL_START, DIAL_END + DIAL_STEP_MB, DIAL_STEP_MB):
            perf = profile_sensitivity(size_mb)
            f.write(f"{size_mb} {perf}\n")


if __name__ == "__main__":
    profile_reporter()
