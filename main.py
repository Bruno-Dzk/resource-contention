import profile_workload
import profile_reporter
import contentiousness
import prediction
import validation
from spec import SpecWorkload

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

def main():
    profile_reporter.profile_reporter()
    workloads = [SpecWorkload(name, size="train") for name in SPEC_NAMES]
    profile_workload.profile_sensitivity(workloads)
    reporter = rp.AveragingReporter("reporters/reporter")
    profile_workload.profile_contentiousness(workloads, reporter)
    contentiousness.generate_scores()
    prediction.calculate_predictions()
    validation.validate_predictions()

if __name__ == '__main__':
    main()