from typing import Final

RESULTS_DIR: Final[str] = "experiment_results/testing"
WORKLOAD_UNDER_PROFILING_CORES: Final[str] = "0-2"
WORKLOAD_IN_BACKGROUND_CORES: Final[str] = "3-5"

# Reporter and SoI dial constants
REPORTER_CORES: Final[str] = "0"
DIAL_START_MB: Final[int] = 0
DIAL_STEP_MB: Final[int] = 4
DIAL_END_MB: Final[int] = 112

# MDS constants
MDS_PROFILING_TIME_S: Final[int] = 300
MDS_STARTUP_WAIT_TIME_S: Final[int] = 120

# Kubernetes workload node names
PROFILING_NODE_NAME: Final[str] = "mc-c6"
REMOTE_NODE_NAME: Final[str] = "mc-b8"