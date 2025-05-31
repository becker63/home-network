import pytest
from typing import List

from lib import PROJECT_ROOT
from lib.group import GroupKey
from lib.find_kcl_files import find_kcl_files

from project_config import ProjectFilters, FILTER_MAP

def get_group_for_member(member: ProjectFilters) -> GroupKey:
    for group in FILTER_MAP:
        if member in group:
            return group
    raise ValueError(f"No group found containing {member}")

def get_groups_for_filter(filter_name: ProjectFilters) -> List[GroupKey]:
    return [group for group in FILTER_MAP if filter_name in group]

def validate_filters_compatible(filters: List[ProjectFilters]) -> None:
    groups_per_filter = [set(get_groups_for_filter(f)) for f in filters]
    if not groups_per_filter:
        raise RuntimeError(f"No groups found for filters {filters}")
    common_groups = set.intersection(*groups_per_filter)
    if not common_groups:
        raise RuntimeError(
            f"\n\n{filters}\n\n"
            "belong to different groups with different filter functions.\n\n"
            "Cannot parametrize tests across incompatible filter groups.\n\n"
            "Try making the lambdas the same."
        )

def fileset(filters: List[ProjectFilters]):
    validate_filters_compatible(filters)

    params = []
    seen_paths = set()

    for filter_name in filters:
        group = get_group_for_member(filter_name)
        filter_fn = FILTER_MAP[group]
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)

        for kf in files:
            if kf.path in seen_paths:
                continue
            seen_paths.add(kf.path)

            rel_path = kf.path.relative_to(PROJECT_ROOT)
            test_id = f"{filter_name.value}::{rel_path}"

            params.append(
                pytest.param(
                    filter_name,
                    kf,
                    id=test_id,
                    marks=pytest.mark.__getattr__(filter_name.value)
                )
            )

    def decorator(func):
        for filter_name in filters:
            func = pytest.mark.__getattr__(filter_name.value)(func)
        return pytest.mark.parametrize("filter_name,kf", params)(func)

    return decorator
