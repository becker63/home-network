from typing import Callable, Any, TypeAlias
import pytest

from lib.config_interface import FILTERS, ProjectFilters, KFile
from lib.find_kcl_files import find_kcl_files

TestFunc: TypeAlias = Callable[[ProjectFilters, KFile], None]
Decorator: TypeAlias = Callable[[TestFunc], TestFunc]
TestCase: TypeAlias = Any  # pytest.param(...) is dynamically typed

def parametrize_kcl_files(
    *filters: ProjectFilters, print_debug: bool = False
) -> Decorator:
    def decorator(func: TestFunc) -> TestFunc:
        cases: list[TestCase] = []

        for pf in filters:
            filter_fn = FILTERS[pf]
            for kf in find_kcl_files(filter_fn=filter_fn, print_debug=print_debug):
                case_id = f"{pf.value}::{kf.path.stem}"
                cases.append(pytest.param(pf, kf, id=case_id))

        return pytest.mark.parametrize("pf, kf", cases)(func)

    return decorator
