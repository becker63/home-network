from typing import Callable, Dict, List
import pytest
from lib.find_kcl_files import find_kcl_files
from lib.common import KFile, FILTER_MAP, GroupKey, ProjectFilters

# Type aliases
FilterFunction = Callable[[KFile], bool]
GroupedFilterMap = Dict[GroupKey, FilterFunction]
FlatFilterFilesMap = Dict[ProjectFilters, List[KFile]]

@pytest.fixture(scope="session")
def kcl_file_filters() -> GroupedFilterMap:
    """
    Provides the grouped filter map used to select KCL files by group keys.
    """
    return FILTER_MAP


@pytest.fixture(scope="session")
def kcl_files_by_filter(kcl_file_filters: GroupedFilterMap) -> FlatFilterFilesMap:
    """
    Uses the filter functions from FILTER_MAP to find matching KCL files.
    Maps individual ProjectFilters members to their files by expanding groups.
    """
    result: FlatFilterFilesMap = {}
    for group_key, filter_fn in kcl_file_filters.items():
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
        for filter_name in group_key:
            result[filter_name] = files
    return result
