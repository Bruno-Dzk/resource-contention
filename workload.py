class Workload():

    def __init__(self, name: str):
        self.name = name

    def run_once(self, cores: str) -> float:
        pass

    def run(self, cores: str) -> None:
        pass

    def stop(self) -> None:
        pass
