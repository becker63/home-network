from dataclasses import dataclass
from pathlib import Path
from enum import Enum, StrEnum
from typing import Dict, Callable, List, Iterator
from .helpers import find_project_root

# ─────────────────────────────
# Types
# ─────────────────────────────

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

@dataclass
class KFile:
    path: Path
    dirname: DirEnum

# StrEnum used to allow clean string comparisons and filter IDs
class ProjectFilters(StrEnum):
    BOOTSTRAP = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM = "random"

# Custom key wrapper to support grouping filters with hashable keys
class GroupKey:
    def __init__(self, *members: ProjectFilters):
        self.members: List[ProjectFilters] = list(members)

    def __iter__(self) -> Iterator[ProjectFilters]:
        return iter(self.members)

    def __getitem__(self, idx):
        return self.members[idx]

    def __hash__(self):
        return hash(frozenset(self.members))

    def __eq__(self, other):
        return isinstance(other, GroupKey) and set(self.members) == set(other.members)

    def __repr__(self):
        return f"GroupKey({', '.join(m.value for m in self.members)})"

def group(*args: ProjectFilters) -> GroupKey:
    return GroupKey(*args)

# ─────────────────────────────
# Constants
# ─────────────────────────────

# Grouped test filters: group(...) creates a GroupKey used in FILTER_MAP
FILTER_MAP: Dict[GroupKey, Callable[[KFile], bool]] = {
    group(ProjectFilters.BOOTSTRAP, ProjectFilters.BOOTSTRAP_SYNTH): lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    group(ProjectFilters.RANDOM): lambda kf: True
}

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()
