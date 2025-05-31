# lib/grouping.py
from typing import List, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from project_config import ProjectFilters

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
