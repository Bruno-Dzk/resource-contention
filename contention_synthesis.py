import subprocess
import os
import logging

logger = logging.getLogger(__name__)

BUILD_DIR = "build"

class Sledge():    
    ELEM_SIZE = 8

    def __init__(self, size_mb: int):
        self.size = size_mb * 1_000_000 // Sledge.ELEM_SIZE
        os.makedirs(BUILD_DIR, exist_ok=True)
        subprocess.run(
            [
                "gcc",
                "-O2",
                "-fopenmp",
                f"-DLBM_SIZE={self.size}",
                "sledge.c",
                "-o",
                f"{BUILD_DIR}/sledge.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.proc = None

    def run(self, cores: str) -> None:
        logger.info(f"Running sledge with footprint size {self.size}")
        self.proc = subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                f"{cores}",
                f"./{BUILD_DIR}/sledge.out",
            ],
            stdin=subprocess.DEVNULL,
        )
    
    def stop(self) -> None:
        if not self.proc:
            logger.warning("An attempt to stop sledge was made but no process was found")
            return
        os.kill(self.proc.pid, 9)

class Bubble():
    ELEM_SIZE = 8

    def __init__(self, size_mb: int):
        self.size = size_mb * 1_000_000 // Bubble.ELEM_SIZE
        os.makedirs(BUILD_DIR, exist_ok=True)
        subprocess.run(
            [
                "gcc",
                "-O3",
                "-fopenmp",
                "-march=native",
                f"-DFOOTPRINT_SIZE={self.size}",
                "-DBUBBLE_TYPE=0",
                "-DNUM_THREADS=3",
                "bubble.c",
                "-o",
                f"{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "gcc",
                "-O3",
                "-fopenmp",
                "-march=native",
                f"-DFOOTPRINT_SIZE={self.size}",
                "-DBUBBLE_TYPE=1",
                "-DNUM_THREADS=2",
                "bubble.c",
                "-o",
                f"{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.proc1 = None
        self.proc2 = None

    def run(self) -> None:
        logger.info(f"Running bubble with footprint size {self.size}")
        self.proc1 = subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "3-5",
                f"./{BUILD_DIR}/bubble_stream.out",
            ],
            stdin=subprocess.DEVNULL,
        )
        self.proc2 = subprocess.Popen(
            [
                "sudo",
                "nice",
                "-n",
                "-20",
                "taskset",
                "-c",
                "6-7",
                f"./{BUILD_DIR}/bubble_rand.out",
            ],
            stdin=subprocess.DEVNULL,
        )
    
    def stop(self) -> None:
        if not self.proc1 and not self.proc2:
            logger.warning("An attempt to stop bubble was made but no process was found")
            return
        os.kill(self.proc1.pid, 9)
        os.kill(self.proc2.pid, 9)