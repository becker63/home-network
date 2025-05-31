import pytest
from functools import wraps
from typing import Callable, Optional
from lib.find_kcl_files import find_kcl_files
from lib.proj_types import KFile
from project_config import ProjectFilters, FILTERS

def parametrize_kcl_files(*filters: ProjectFilters, print_debug: bool = False):
    """
    Parametrize test with (pf, kf) pairs, unpacked into two args.
    """
    def decorator(func):
        cases = []
        for pf in filters:
            filter_fn = FILTERS[pf]
            for kf in find_kcl_files(filter_fn=filter_fn, print_debug=print_debug):
                case_id = f"{pf.value}::{kf.path.stem}"
                cases.append(pytest.param(pf, kf, id=case_id))

        return pytest.mark.parametrize("pf, kf", cases)(func)

    return decorator
