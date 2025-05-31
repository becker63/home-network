import pytest
from typing import List, Set
from lib.find_kcl_files import find_kcl_files
from project_config import ProjectFilters, GroupKey, PARENT_FILTER_MAP
from lib import PROJECT_ROOT

def fileset(filters: List[ProjectFilters]):

    if not filters:
        raise ValueError("Must provide at least one filter")

    filter_set = set(filters)

    # Find all group keys that contain at least one filter in filters
    matched_groups = []
    for parent_name, group_list in PARENT_FILTER_MAP.items():
        for group_key, filter_fn in group_list:
            if filter_set.intersection(set(group_key.members)):
                matched_groups.append((parent_name, group_key, filter_fn))

    if not matched_groups:
        raise RuntimeError(f"No groups matched for filters {filters}")

    # Aggregate unique files from all matched groups
    unique_files = {}
    for parent_name, group_key, filter_fn in matched_groups:
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
        for kf in files:
            unique_files[kf.path] = kf

    files = list(unique_files.values())

    # Use the first filter for marking and id prefix
    first_filter = filters[0]

    params = []
    for kf in files:
        rel_path = kf.path.relative_to(PROJECT_ROOT)
        test_id = f"{first_filter.value}::{rel_path}"
        params.append(
            pytest.param(
                first_filter,
                kf,
                id=test_id,
                marks=[pytest.mark.__getattr__(first_filter.value)],
            )
        )

    def decorator(func):
        if not params:
            return func
        # Mark the test function with the first filter
        func = pytest.mark.__getattr__(first_filter.value)(func)

        # Parametrize test with all files
        return pytest.mark.parametrize("filter_name,kf", params)(func)

    return decorator
