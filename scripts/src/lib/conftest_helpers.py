import pytest
from lib.helpers import find_project_root
from kcl_tasks.filters import ProjectFilters, FILTER_MAP
from lib.common import GroupKey, KFile
from lib.find_kcl_files import find_kcl_files

def get_group_for_member(member: ProjectFilters) -> GroupKey:
    for group in FILTER_MAP:
        if member in group:
            return group
    raise ValueError(f"No group found containing {member}")

def parametrize_files_for_group(filters: list[ProjectFilters]):
    params = []
    ids = []

    for filter_name in filters:
        group = get_group_for_member(filter_name)
        filter_fn = FILTER_MAP[group]
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
        for kf in files:
            rel_path = kf.path.relative_to(find_project_root())
            test_id = f"{filter_name.value}::{rel_path}"
            # Use pytest.param to attach mark to each param
            params.append(
                pytest.param(
                    filter_name,
                    kf,
                    id=test_id,
                    marks=pytest.mark.__getattr__(filter_name.value)
                )
            )
            ids.append(test_id)  # ids not necessary here but kept for clarity

    return pytest.mark.parametrize("filter_name,kf", params)
