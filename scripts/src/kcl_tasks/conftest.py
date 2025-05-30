from typing import Callable, Dict, List
import pytest
from lib.find_kcl_files import find_kcl_files
from lib.common import KFile, FILTER_MAP, GroupKey, ProjectFilters

# Type aliases for clarity
FilterFunction = Callable[[KFile], bool]
GroupedFilterMap = Dict[GroupKey, FilterFunction]
FlatFilterFilesMap = Dict[ProjectFilters, List[KFile]]


# ---------------------------------------------
# Fixtures for dependency injection in tests
# ---------------------------------------------

@pytest.fixture(scope="session")
def kcl_file_filters() -> GroupedFilterMap:
    """
    Provides a map of grouped filter functions.
    Used to select KCL files based on high-level groups (e.g., 'bootstrap').
    """
    return FILTER_MAP


@pytest.fixture(scope="session")
def kcl_files_by_filter(kcl_file_filters: GroupedFilterMap) -> FlatFilterFilesMap:
    """
    Applies each filter in each group to find matching KCL files,
    then flattens the results by individual filter name (ProjectFilters).
    """
    result: FlatFilterFilesMap = {}
    for group_key, filter_fn in kcl_file_filters.items():
        files = find_kcl_files(filter_fn=filter_fn, print_debug=False)
        for filter_name in group_key:
            result[filter_name] = files
    return result


# ---------------------------------------------
# Internal hook logic for keyword expansion
# ---------------------------------------------

def _expand_k_expr(k_expr: str) -> str:
    """
    Expands -k keyword expressions like 'bootstrap_synth'
    into a logical OR of all filters in that group:
    e.g. 'bootstrap or bootstrap_synth'

    This ensures all related tests are discovered and run.
    """
    if not k_expr:
        return k_expr

    # Find filters that appear in the given -k expression
    matched_filters = [f for f in ProjectFilters if f.value in k_expr]
    if not matched_filters:
        return k_expr

    # Collect all filter values from matching groups
    expanded_filters = set()
    for group_key in FILTER_MAP:
        if any(f in group_key for f in matched_filters):
            expanded_filters.update(f.value for f in group_key)

    return " or ".join(sorted(expanded_filters))


# ---------------------------------------------
# Pytest configuration hooks
# ---------------------------------------------

def pytest_addoption(parser):
    """
    Required so config.option.keyword is initialized early.
    Even though this does nothing directly, it ensures `-k` is available for patching.
    """
    pass


def pytest_configure(config):
    """
    Expands grouped keyword expressions automatically before collection starts.
    Replaces `-k bootstrap_synth` with `-k "bootstrap or bootstrap_synth"` internally.
    """
    original_k = getattr(config.option, "keyword", "")
    expanded = _expand_k_expr(original_k)
    if expanded and expanded != original_k:
        config.option.keyword = expanded
