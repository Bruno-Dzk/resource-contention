import profile_workload
import profile_reporter
import contentiousness
import prediction
import validation
import time
import pathlib
from spec import SpecWorkload
from mds import MdsFactory, MdsClient
from kube_workload import KubeWorkload
from typing import List
import logging
from cpu_freq import CpuFreqPolicy, Governor
from typing import Callable

import reporter as rp

SPEC_NAMES = [
    "600.perlbench_s",
    "602.gcc_s",
    "605.mcf_s",
    "620.omnetpp_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "631.deepsjeng_s",
    "641.leela_s",
    "648.exchange2_s",
    "657.xz_s",
    "603.bwaves_s",
    "607.cactuBSSN_s",
    "619.lbm_s",
    "627.cam4_s",
    "628.pop2_s",
    "638.imagick_s",
    "644.nab_s",
    "649.fotonik3d_s",
    "654.roms_s",
]

MDS_SERVICES = ["datatest", "dataforwarding", "datageneration", "etcd"]

MDS_UNDER_PROFILING = ["datatest", "dataforwarding", "datageneration"]

GOVERNOR = Governor.PERFORMANCE

def main():
    print("HELLO")
    # logging.getLogger().setLevel(logging.DEBUG)

    # mds_factory = MdsFactory()
    # all_workloads: List[KubeWorkload] = [
    #     mds_factory.create_workload(name) for name in MDS_SERVICES
    # ]
    # for workload in all_workloads:
    #     workload.setup()
    # workloads = [w for w in all_workloads if w.name in MDS_UNDER_PROFILING]
    # workloads_under_profiling = [w for w in workloads if w.name in MDS_UNDER_PROFILING]
    # profile_workload.profile_sensitivity(workloads_under_profiling)
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    CpuFreqPolicy.set_governor(GOVERNOR)
    spec_experiment()
    CpuFreqPolicy.reset_governor()
    
def spec_experiment():
    # SPEC 
    workloads = [SpecWorkload(name) for name in SPEC_NAMES]
    reporter = rp.AveragingReporter("reporters/reporter")
    profile_reporter.profile_reporter(reporter)
    profile_workload.profile_sensitivity(workloads)
    profile_workload.profile_contentiousness(workloads, reporter)
    contentiousness.generate_scores()
    prediction.calculate_predictions()
    validation.validate_predictions(workloads)
    # for wokload in all_workloads:
    #     wokload.tear_down()

if __name__ == "__main__":
    mds_factory = MdsFactory()
    all_workloads: List[KubeWorkload] = [
        mds_factory.create_workload(name) for name in MDS_SERVICES
    ]
    for workload in all_workloads:
        workload.setup()
