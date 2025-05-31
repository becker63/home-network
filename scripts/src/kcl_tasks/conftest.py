from typing import Callable, Dict, List, Tuple
import pytest

from lib import find_kcl_files
from lib import KFile, GroupKey

from project_config import ProjectFilters, PARENT_FILTER_MAP

FilterFunction = Callable[[KFile], bool]
GroupFilterTuple = Tuple[GroupKey, FilterFunction]
ParentFilterMap = Dict[str, List[GroupFilterTuple]]
FlatFilterFilesMap = Dict[ProjectFilters, List[KFile]]


def pytest_configure(config):
    # Register individual filter marks
    for pf in ProjectFilters:
        config.addinivalue_line(
            "markers", f"{pf.value}: auto-registered mark from ProjectFilters enum"
        )
    # Register parent marks from PARENT_FILTER_MAP keys
    for parent_name in PARENT_FILTER_MAP.keys():
        config.addinivalue_line(
            "markers", f"{parent_name}: auto-registered parent group mark"
        )

@pytest.fixture(scope="session")
def kcl_file_filters() -> ParentFilterMap:
    return PARENT_FILTER_MAP

@pytest.fixture(scope="session")
def kcl_files_by_filter(kcl_file_filters: ParentFilterMap) -> FlatFilterFilesMap:
    result: FlatFilterFilesMap = {}
    seen_files = set()

    for group_list in kcl_file_filters.values():
        for group_key, filter_fn in group_list:
            files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
            for filter_name in group_key:
                if filter_name not in result:
                    result[filter_name] = []
                for f in files:
                    if f.path not in seen_files:
                        result[filter_name].append(f)
                        seen_files.add(f.path)
    return result
