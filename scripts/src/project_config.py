from enum import Enum, StrEnum
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from lib.group import GroupKey, group
from lib.proj_types import KFile
from lib.find_proj_root import find_project_root

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM = "random"

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()

# Single unified map:
# Parent key -> List of (GroupKey, filter function)
PARENT_FILTER_MAP: Dict[str, List[Tuple[GroupKey, Callable[[KFile], bool]]]] = {
    "bootstrap_root": [
        (
            group(ProjectFilters.BOOTSTRAP, ProjectFilters.BOOTSTRAP_SYNTH),
            lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
        )
    ],
    "random": [
        (
            group(ProjectFilters.RANDOM),
            lambda kf: True,
        )
    ],
}
