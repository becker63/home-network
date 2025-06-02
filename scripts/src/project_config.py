# src/project_config.py

from collections.abc import Callable
from enum import Enum, StrEnum
from pathlib import Path

from config.schema import KFile
from lib.find_proj_root import find_project_root


class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT:       Path = (PROJECT_ROOT / "kcl").resolve()

FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname.value == "bootstrap",
    ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname.value == "bootstrap",
    ProjectFilters.RANDOM:           lambda _kf: True,
}
