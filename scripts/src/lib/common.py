from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, List, Iterator, TYPE_CHECKING, Dict
from .helpers import find_project_root

# If you import ProjectFilters directly at runtime in common.py, it causes a circular import problem (because filters.py imports common.py and vice versa).
# This means the import inside if TYPE_CHECKING: only happens during static type checking — no runtime import occurs, so no circular import or runtime error.
if TYPE_CHECKING:
    from kcl_tasks.filters import ProjectFilters

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

# Custom key wrapper to support grouping filters with hashable keys
class GroupKey:
    def __init__(self, *members: 'ProjectFilters'):
        self.members: List['ProjectFilters'] = list(members)

    def __iter__(self) -> Iterator['ProjectFilters']:
        return iter(self.members)

    def __getitem__(self, idx):
        return self.members[idx]

    def __hash__(self):
        return hash(frozenset(self.members))

    def __eq__(self, other):
        return isinstance(other, GroupKey) and set(self.members) == set(other.members)

    def __repr__(self):
        return f"GroupKey({', '.join(m.value for m in self.members)})"

def group(*args: 'ProjectFilters') -> GroupKey:
    return GroupKey(*args)

# ─────────────────────────────
# Constants
# ─────────────────────────────

# Delay the import to avoid circular dependency
def get_filter_map() -> Dict[GroupKey, Callable[[KFile], bool]]:
    from kcl_tasks.filters import FILTER_MAP
    return FILTER_MAP

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()
