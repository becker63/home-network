from typing import List
import pytest
from .find_kcl_files import find_kcl_files
from .common import GroupKey
from kcl_tasks.filters import ProjectFilters, FILTER_MAP
from .helpers import find_project_root
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

def parametrize_files_for_group(filters: List[ProjectFilters]):
    """
    Parametrize the test on individual KFiles that belong to the specified ProjectFilters.
    Handles group expansion the same way as `parametrize_group`, but yields (filter_name, KFile).
    """
    selected = os.getenv("PYTEST_CURRENT_TEST", "")
    if any(f.value in selected for f in filters[1:]):
        selected_filters = filters  # run all
    else:
        selected_filters = [filters[0]]  # run default

    # Flattened list of (filter_name, KFile)
    params = []
    ids = []
    for filter_name in selected_filters:
        group = get_group_for_member(filter_name)
        filter_fn = FILTER_MAP[group]
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
        for kf in files:
            params.append((filter_name, kf))
            rel_path = kf.path.relative_to(find_project_root())
            ids.append(f"{filter_name.value}::{rel_path}")

    return pytest.mark.parametrize("filter_name,kf", params, ids=ids)
