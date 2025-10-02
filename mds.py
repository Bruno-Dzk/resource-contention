import argparse
import json
from typing import List
import logging
from datetime import datetime, timezone
from websocket import create_connection
import pathlib
from kube_controller import KubeController
from kube_workload import KubeWorkload

class MdsFactory:
    METRICS = {
        "datageneration": "datageneration_datagen_req_duration_bucket",
        "dataforwarding": "dataforwarding_datafwd_req_duration_bucket",
        "datatest": "datatest_datatest_req_duration_bucket"
    }

    YAML_ROOT = pathlib.Path("mds/yaml")

    PROFILING_TIME_S = 300

    def __init__(self):
        self.controller = KubeController()
    
    def create_workload(self, mds_service_name: str, is_required: bool = True) -> KubeWorkload:
        metric = MdsFactory.METRICS.get(mds_service_name, None)
        yaml_file_name = f"{mds_service_name}.yaml"
        return KubeWorkload(
            mds_service_name,
            MdsFactory.YAML_ROOT / yaml_file_name,
            self.controller,
            is_required,
            MdsFactory.PROFILING_TIME_S,
            metric_name=metric
        )
        

class MdsClient:
    # HOST = "o2n-ide"
    HOST = "145.100.131.48"

    def __init__(self):
        url = f"ws://{MdsClient.HOST}:31001/delivery/control/api/"
        #logging.info(f"Connection: {url}")
        self.ws = create_connection(url)

    def send_commands(self, commands_file: pathlib.Path):
        commands = self._load_cmds_from_file(commands_file)
        self.ws.send(commands)
        result = self.ws.recv()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        print(exc_type, exc_value)
        self.ws.close()
        #logging.info("Connetion closed")

    def _load_cmds_from_file(self, cmd_file: pathlib.Path) -> str:
        with open(cmd_file, 'r') as fd:
            commands = json.load(fd)
            d = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            return json.dumps({
                "header": {
                    "oid":"1.5.2.3.4.2.1003",
                    "tid": "e8e711bc-1d0c-418c-b6e4-d4119db1af30",
                    "timestampe": d
                },
                "commands": commands 
                })
        
def main():
    pass

if __name__ == "__main__":
    main()