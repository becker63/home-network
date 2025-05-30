from typing import List
import pytest

from lib.common import KFile
from kcl_tasks.filters import ProjectFilters

# Use the kcl_files_by_filter fixture to parametrize tests based on filters

def parametrize_files_for_group(filters: List[ProjectFilters]):
    """
    Parametrize a test on individual KFiles for the given list of ProjectFilters.
    Relies on the kcl_files_by_filter fixture to get the files.
    """

    @pytest.fixture(scope="function")
    def _params(request, kcl_files_by_filter):
        params = []
        ids = []
        for pf in filters:
            files = kcl_files_by_filter.get(pf, [])
            for kf in files:
                params.append((pf, kf))
                # Use filter value + relative path as the test id
                rel_path = kf.path.relative_to(kf.path.anchor)  # or your project root if you want
                ids.append(f"{pf.value}::{rel_path}")

        # Attach parameter list and ids to the test function dynamically
        return pytest.mark.parametrize("filter_name,kf", params, ids=ids)(request.function)

    return _params
