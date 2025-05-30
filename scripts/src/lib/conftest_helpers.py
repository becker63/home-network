from typing import Callable, Dict, List, Iterable
import pytest
from .find_kcl_files import find_kcl_files
from .common import KFile, FILTER_MAP, GroupKey, ProjectFilters

def get_group_for_member(member: ProjectFilters) -> GroupKey:
    """
    Find the GroupKey from FILTER_MAP that contains the given ProjectFilters member.
    Raises ValueError if none found.
    """
    for group in FILTER_MAP:
        if member in group:
            return group
    raise ValueError(f"No group found containing {member}")


def parametrize_group(member: ProjectFilters):
    """
    Given one ProjectFilters member, find the full group and parametrize on
    all individual ProjectFilters members in that group.
    """
    group = get_group_for_member(member)
    return pytest.mark.parametrize(
        "filter_name",
        list(group),
        ids=[f.value for f in group],
    )
