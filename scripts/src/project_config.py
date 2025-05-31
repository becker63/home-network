from enum import Enum, StrEnum
from pathlib import Path
from typing import Dict, Callable

from lib.group import GroupKey, group
from lib.proj_types import KFile
from lib.find_proj_root import find_project_root

class ProjectConfig:
    # The actual paths in kcl we're filtering
    class DirEnum(Enum):
        BOOTSTRAP = "bootstrap"
        FRP_SCHEMA = "frp_schema"
        SCHEMAS = "schemas"
        DEFAULT = "default"

    # Test names for pytest
    class ProjectFilters(StrEnum):
        BOOTSTRAP = "bootstrap"
        BOOTSTRAP_SYNTH = "bootstrap_synth"
        RANDOM = "random"

    PROJECT_ROOT: Path = find_project_root()
    KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()

    FILTER_MAP: Dict[GroupKey, Callable[[KFile], bool]] = {
        # We
        group(
            ProjectFilters.BOOTSTRAP,
            ProjectFilters.BOOTSTRAP_SYNTH
        ): lambda kf: kf.dirname == ProjectConfig.DirEnum.BOOTSTRAP,

        group(
            ProjectFilters.RANDOM
        ): lambda kf: True,
    }



# Export for use in our project.. pretty ugly.
ProjectFilters = ProjectConfig.ProjectFilters
DirEnum = ProjectConfig.DirEnum
FILTER_MAP = ProjectConfig.FILTER_MAP
PROJECT_ROOT = ProjectConfig.PROJECT_ROOT
KCL_ROOT = ProjectConfig.KCL_ROOT
