from workload import Workload
from kube_controller import KubeController
from typing import Optional
from metrics import query_latency
import pathlib
import time


class KubeWorkload(Workload):
    PROFILING_NODE_NAME = "mc-c6"
    REMOTE_NODE_NAME = "mc-b8"

    def __init__(
        self,
        name: str,
        yaml_path: pathlib.Path,
        controller: KubeController,
        is_required: bool,
        profiling_time_s: int,
        metric_name: Optional[str] = None,
    ):
        self.controller = controller
        self.is_required = is_required
        self.yaml_path = yaml_path
        self.profiling_time_s = profiling_time_s
        self.metric_name = metric_name
        self.deployed_on: Optional[str] = None
        super().__init__(name)

    def setup(self):
        if self.is_required and self.deployed_on is None:
            self.controller.deploy_application(
                self.name, self.yaml_path, KubeWorkload.REMOTE_NODE_NAME
            )
        self.deployed_on = KubeWorkload.REMOTE_NODE_NAME

    def tear_down(self):
        self.controller.remove_application(self.name)

    def _deploy_on_profiling_node(self) -> None:
        if self.deployed_on == KubeWorkload.PROFILING_NODE_NAME:
            return
        if self.deployed_on is not None:
            self.controller.remove_application(self.name)
        self.controller.deploy_application(
            self.name, self.yaml_path, KubeWorkload.PROFILING_NODE_NAME
        )
        self.deployed_on = KubeWorkload.PROFILING_NODE_NAME

    def profile(self, cores: str) -> float:
        try:
            self._deploy_on_profiling_node()
            # Wait for the microservices to be ready
            time.sleep(120)
            if not self.metric_name:
                raise Exception(f"Profiling of workload {self.name} is not supported")
            time.sleep(self.profiling_time_s)
            return query_latency(self.metric_name, self.profiling_time_s)
        finally:
            self.stop()

    def run_in_background(self, cores) -> None:
        if self.deployed_on != KubeWorkload.PROFILING_NODE_NAME:
            self._deploy_on_profiling_node()

    def stop(self) -> None:
        self.controller.remove_application(self.name)
        if self.is_required:
            self.controller.deploy_application(
                self.name, self.yaml_path, KubeWorkload.REMOTE_NODE_NAME
            )
