from typing import Callable, Dict, List
import pytest

from lib import find_kcl_files
from lib import KFile, GroupKey

from .filters import ProjectFilters, FILTER_MAP

FilterFunction = Callable[[KFile], bool]
GroupedFilterMap = Dict[GroupKey, FilterFunction]
FlatFilterFilesMap = Dict[ProjectFilters, List[KFile]]

# Register marks dynamically so pytest recognizes all ProjectFilters without warnings
def pytest_configure(config):
    for pf in ProjectFilters:
        config.addinivalue_line(
            "markers", f"{pf.value}: auto-registered mark from ProjectFilters enum"
        )

@pytest.fixture(scope="session")
def kcl_file_filters() -> Dict[GroupKey, Callable[[KFile], bool]]:
    return FILTER_MAP

@pytest.fixture(scope="session")
def kcl_files_by_filter(kcl_file_filters: GroupedFilterMap) -> FlatFilterFilesMap:
    result: FlatFilterFilesMap = {}
    seen_files = set()

    for group_key, filter_fn in kcl_file_filters.items():
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)

        # Assign each file only once to the first filter in the group
        for filter_name in group_key:
            if filter_name not in result:
                result[filter_name] = []
            for f in files:
                if f.path not in seen_files:
                    result[filter_name].append(f)
                    seen_files.add(f.path)
    return result
