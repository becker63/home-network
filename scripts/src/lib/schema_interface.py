from typing import TypeVar, Generic, Protocol, Callable
from pathlib import Path
from enum import Enum, StrEnum
from pydantic import BaseModel, ConfigDict
from .find_proj_root import find_project_root

# === CONSTANT: PROJECT_ROOT only ===
PROJECT_ROOT: Path = find_project_root()

# === GENERIC KFile MODEL ===
Dir = TypeVar("Dir", bound=Enum)

class KFile(BaseModel, Generic[Dir]):
    model_config = ConfigDict(frozen=True)
    path: Path
    dirname: Dir

# === PROTOCOL: ProjectSchema Interface ===
Filter = TypeVar("Filter", bound=StrEnum)

class ProjectSchema(Protocol[Dir, Filter]):
    DirEnum: type[Dir]
    ProjectFilters: type[Filter]
    KFile: type[KFile[Dir]]

    def get_filters(self) -> dict[Filter, Callable[[object], bool]]:
        ...
