from typing import Dict, Callable
from enum import StrEnum

from lib import GroupKey,group
from lib import DirEnum, KFile


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
