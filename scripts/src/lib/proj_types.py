# lib/types.py

from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

@dataclass
class KFile:
    path: Path
    dirname: DirEnum
