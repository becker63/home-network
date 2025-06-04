from pathlib import Path
from enum import Enum, StrEnum

from lib.config_interface import PROJECT_ROOT, KFile

KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()

class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

from lib.config_interface import ProjectSchema

class MyProjectSchema(ProjectSchema[DirEnum, ProjectFilters]):
    DirEnum = DirEnum
    ProjectFilters = ProjectFilters
    KFile = KFile[DirEnum]  # bind the generic to DirEnum

    def get_filters(self):
        return {
            ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
            ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
            ProjectFilters.RANDOM:           lambda _kf: True,
        }
