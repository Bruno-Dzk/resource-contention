from workload import Workload
import kubernetes as kube
import pathlib
import yaml
import time
import metrics
from abc import ABC, abstractmethod

class Resource(ABC):
    @abstractmethod
    def __init__(self, client: kube.client.ApiClient, doc: dict):
        pass
    @abstractmethod
    def create():
        pass
    @abstractmethod
    def delete():
        pass

class StatefulSet(Resource):
    def __init__(self, client: kube.client.ApiClient, doc: dict):
        self.apps = kube.client.AppsV1Api(client)
        self.doc = doc
        self.name = doc['metadata']['name']
    def create(self):
        try:
            self.delete()
        except kube.client.ApiException as e:
            if e.status != 404:
                raise
        print(f"Creating StatefulSet {self.name}")
        self.apps.create_namespaced_stateful_set("default", body=self.doc)
    def delete(self):
        print(f"Deleting StatefulSet {self.name}")
        self.apps.delete_namespaced_stateful_set(self.name, "default")

class Service(Resource):
    def __init__(self, client: kube.client.ApiClient, doc: dict):
        self.core = kube.client.CoreV1Api(client)
        self.doc = doc
        self.name = doc['metadata']['name']
    def create(self):
        try:
            self.delete()
        except kube.client.ApiException as e:
            if e.status != 404:
                raise
        print(f"Creating Service {self.name}")
        self.core.create_namespaced_service("default", body=self.doc)
    def delete(self):
        print(f"Deleting Service {self.name}")
        self.core.delete_namespaced_service(self.name, "default")
        
def _create_resouce(client: kube.client.ApiClient, doc: dict) -> Resource:
    match(doc['kind']):
        case 'StatefulSet':
                return StatefulSet(client, doc)
        case 'Service':
            return Service(client, doc)
        case _:
            raise

def _get_resources(client: kube.client.ApiClient, yaml_path: pathlib.Path) -> list[Resource]:
    with open(yaml_path) as f:
        docs = list(yaml.safe_load_all(f))
        return [_create_resouce(client, doc) for doc in docs]

class KubeWorkload(Workload):
    def __init__(
        self,
        name: str,
        client: kube.client.ApiClient,
        yaml_path: pathlib.Path,
        metric_name: str,
    ):
        self.client = client
        self.yaml_path = yaml_path
        self.metric_name = metric_name
        super().__init__(name)

    def run_once(self, cores: str) -> float:
        resources = _get_resources(client, self.yaml_path)
        for resource in resources:
            resource.create()
        time.sleep(90)
        perf = metrics.query_latency(self.metric_name)
        for resource in resources:
            resource.delete()
        return perf

    def run(self, cores: str) -> None:
        pass

    def stop(self) -> None:
        pass


def create_client():
    kube.config.load_kube_config()
    return kube.client.ApiClient()


if __name__ == "__main__":
    client = create_client()
    workload = KubeWorkload(
        "datageneration",
        client,
        pathlib.Path(
            "mds/yaml/datageneration.yaml",
        ),
        "datageneration_datagen_req_duration_count",
    )
    print(workload.run_once("0"))
