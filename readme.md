# Resource Contention
This is an implementation of the Master Thesis: https://www.akesson.nl/files/students/dzikowski-thesis.pdf

## Prerequisites
* Python 3.11+

## Installation

1. Create new virtual env
```shell
python -m venv venv
source venv/bin/activate
```
2. Install dependencies
```shell
pip install -r requirements.txt
```
3. Install Google Benchmark by following https://github.com/google/benchmark?tab=readme-ov-file#installation
4. Move Benchmark to repo root
5. Compile reporters:
```shell
cd reporters
chmod 700 compileReporters.sh
./compileReporters.sh
```

## Kubernetes setup
1. Install (MicroK8S)[https://canonical.com/microk8s/docs/getting-started] on two nodes 
1. Create a multi-node cluster (https://canonical.com/microk8s/docs/clustering)
1. Set registry secret
```
cd mds
./setRegistrySecret.sh <docker-username> <docker-password> <docker-email>
```
4. Follow [prometheus/runbook.md] to setup Prometheus

## Running experiments
Adjust config in `constants.py`. Experiment configuration-as-code can be done in `main.py`.

To run experiments, use `screen`. This is necessary because they take so long that your ssh connection will time out.

Run:

```shell
screen
python main.py
screen -d
```

You can kill the screen after experiment is done:
```shell
screen -ls
screen -XS <screen_name> quit
```