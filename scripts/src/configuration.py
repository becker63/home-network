# src/configuration.py

from enum import StrEnum
from pathlib import Path
from typing import Callable
from pydantic import BaseModel, ConfigDict
from lib.find_proj_root import find_project_root

# === Enum Definitions ===
class DirEnum(StrEnum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"


class ProjectFilters(StrEnum):
    BOOTSTRAP = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM = "random"
    DEFAULT = "default"


# === KFile Model ===
class KFile(BaseModel):
    path: Path
    dirname: DirEnum

    model_config = ConfigDict(frozen=True)


# === Constants ===
PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "kcl").resolve()


FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BOOTSTRAP: lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.BOOTSTRAP_SYNTH: lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.RANDOM: lambda kf: True,
    ProjectFilters.DEFAULT: lambda kf: True,
}
