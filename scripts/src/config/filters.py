from collections.abc import Callable

from config.schema import DirEnum, KFile, ProjectFilters

FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.RANDOM:           lambda _kf: True,
}
