
import pytest

from lib.project_schema_runtime import FILTERS
from lib.project_schema_runtime import ProjectFilters
from lib.find_kcl_files import find_kcl_files


def parametrize_kcl_files(*filters: ProjectFilters, print_debug: bool = False):
    def decorator(func):
        cases = []
        for pf in filters:
            filter_fn = FILTERS[pf]
            for kf in find_kcl_files(filter_fn=filter_fn, print_debug=print_debug):
                case_id = f"{pf.value}::{kf.path.stem}"
                cases.append(pytest.param(pf, kf, id=case_id))
        return pytest.mark.parametrize("pf, kf", cases)(func)

    return decorator
