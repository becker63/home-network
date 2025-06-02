from enum import Enum, StrEnum
from pathlib import Path
from dataclasses import dataclass

class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

@dataclass(frozen=True)
class KFile:
    path: Path
    dirname: DirEnum
