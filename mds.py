import pathlib
from kube_controller import KubeController
from kube_workload import KubeWorkload
from load_generator import MdsLoadGenerator, LoadGenerator

class MdsFactory:
    METRICS = {
        "datageneration": "datageneration_datagen_req_duration_bucket",
        "dataforwarding": "dataforwarding_datafwd_req_duration_bucket",
        "datatest": "datatest_datatest_req_duration_bucket",
        "planner": "planning_planner_schedule_calc_bucket"
    }

    LOAD_GENERATORS: dict[str, LoadGenerator] = {
        "planner": MdsLoadGenerator()
    }

    YAML_ROOT = pathlib.Path("mds/yaml")

    PROFILING_TIME_S = 300

    def __init__(self):
        self.controller = KubeController()
    
    def create_workload(self, mds_service_name: str, is_required: bool = True) -> KubeWorkload:
        metric = MdsFactory.METRICS.get(mds_service_name, None)
        yaml_file_name = f"{mds_service_name}.yaml"
        load_generator = MdsFactory.LOAD_GENERATORS.get(mds_service_name, None)
        return KubeWorkload(
            mds_service_name,
            MdsFactory.YAML_ROOT / yaml_file_name,
            self.controller,
            is_required,
            MdsFactory.PROFILING_TIME_S,
            metric_name=metric,
            load_generator=load_generator
        )