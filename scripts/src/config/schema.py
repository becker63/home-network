from enum import Enum, StrEnum
from pathlib import Path

from pydantic import BaseModel


class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

class KFile(BaseModel):
    path: Path
    dirname: DirEnum

    class Config:
        frozen = True  # makes it hashable / like a dataclass(frozen=True)
