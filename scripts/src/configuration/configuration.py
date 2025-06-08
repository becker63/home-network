from enum import StrEnum, auto
from pathlib import Path
from typing import Callable
from pydantic import BaseModel, ConfigDict
from lib.find_proj_root import find_project_root

class DirEnum(StrEnum):
    CLUSTER = "cluster"
    PROXY = "proxy"
    SCHEMAS = "schemas"
    DEFAULT = "default"


class ProjectFilters(StrEnum):
    BASE = auto()
    PROXY_TEST = auto()
    RANDOM = auto()
    DEFAULT = auto()


class KFile(BaseModel):
    path: Path
    dirname: DirEnum

    model_config = ConfigDict(frozen=True)


PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "kcl").resolve()


FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BASE: lambda kf: kf.dirname == DirEnum.CLUSTER,
    ProjectFilters.PROXY_TEST: lambda kf: kf.dirname == DirEnum.PROXY,
    ProjectFilters.DEFAULT: lambda kf: True,
}
