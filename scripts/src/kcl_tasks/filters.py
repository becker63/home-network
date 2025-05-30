from typing import Dict, Callable
from lib.common import KFile, GroupKey,group, DirEnum
from enum import StrEnum

class ProjectFilters(StrEnum):
    BOOTSTRAP = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM = "random"

FILTER_MAP: Dict[GroupKey, Callable[[KFile], bool]] = {
    group(
        ProjectFilters.BOOTSTRAP,
        ProjectFilters.BOOTSTRAP_SYNTH
    ): lambda kf: kf.dirname == DirEnum.BOOTSTRAP,

    group(
        ProjectFilters.RANDOM
    ): lambda kf: True
}
