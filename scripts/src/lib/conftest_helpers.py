import pytest
from typing import List

from .helpers import find_project_root
from .group import GroupKey
from .find_kcl_files import find_kcl_files

from kcl_tasks.filters import ProjectFilters, FILTER_MAP

def get_group_for_member(member: ProjectFilters) -> GroupKey:
    """
    Find the group key (tuple of filters) that contains the given filter member.
    Raises ValueError if no group contains the member.
    """
    for group in FILTER_MAP:
        if member in group:
            return group
    raise ValueError(f"No group found containing {member}")

def validate_filters_compatible(filters: List[ProjectFilters]) -> None:
    """
    Validate that all given filters belong to at least one common group.
    If no common group exists, raises RuntimeError.
    This ensures filters share the same underlying filter function (lambda).
    """
    groups_per_filter = [set(get_groups_for_filter(f)) for f in filters]

    if not groups_per_filter:
        raise RuntimeError(f"No groups found for filters {filters}")

    # Find intersection of groups sets
    common_groups = set.intersection(*groups_per_filter)
    if not common_groups:
        raise RuntimeError(
            f"\n\n{filters}\n\n"
            "belong to different groups with different filter functions.\n\n"
            "Cannot parametrize tests across incompatible filter groups.\n\n"
            "Try making the lambdas the same."
        )

def get_groups_for_filter(filter_name: ProjectFilters) -> List[GroupKey]:
    """
    Helper to find all groups containing the filter_name.
    """
    return [group for group in FILTER_MAP if filter_name in group]

def parametrize_files_for_group(filters: List[ProjectFilters]):
    """
    Parametrize a test with all files matching any of the requested filters.
    Raises a RuntimeError if the filters have incompatible underlying lambdas.
    """
    # Validate filters before gathering files
    validate_filters_compatible(filters)

    params = []
    ids = []

    for filter_name in filters:
        group = get_group_for_member(filter_name)
        filter_fn = FILTER_MAP[group]
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)

        for kf in files:
            rel_path = kf.path.relative_to(find_project_root())
            test_id = f"{filter_name.value}::{rel_path}"

            # Attach pytest mark dynamically based on filter name
            params.append(
                pytest.param(
                    filter_name,
                    kf,
                    id=test_id,
                    marks=pytest.mark.__getattr__(filter_name.value)
                )
            )
            ids.append(test_id)

    return pytest.mark.parametrize("filter_name,kf", params)
