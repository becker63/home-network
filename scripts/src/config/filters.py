from typing import Callable, Dict
from config.schema import KFile, ProjectFilters, DirEnum

FILTERS: Dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.RANDOM:           lambda _kf: True,
}
