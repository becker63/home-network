from typing import Callable, Dict, List, Iterable
import pytest
from .find_kcl_files import find_kcl_files
from .common import KFile, FILTER_MAP, GroupKey, ProjectFilters
import os

def get_group_for_member(member: ProjectFilters) -> GroupKey:
    """
    Find the GroupKey from FILTER_MAP that contains the given ProjectFilters member.
    Raises ValueError if none found.
    """
    for group in FILTER_MAP:
        if member in group:
            return group
    raise ValueError(f"No group found containing {member}")


def parametrize_group(filters: List[ProjectFilters]):
    """
    Parametrize on a list of ProjectFilters.
    By default, only the first filter will run to avoid duplicate test runs.
    If any filter in the group is mentioned in PYTEST_CURRENT_TEST (via -k), run all.
    """
    selected = os.getenv("PYTEST_CURRENT_TEST", "")
    if any(f.value in selected for f in filters[1:]):
        # Explicit selection detected; run all
        selected_filters = filters
    else:
        # Default run: only first filter
        selected_filters = [filters[0]]

    return pytest.mark.parametrize(
        "filter_name",
        selected_filters,
        ids=[f.value for f in selected_filters],
    )
