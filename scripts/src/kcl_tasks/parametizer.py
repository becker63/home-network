from typing import Callable, Any, TypeAlias
import pytest
from pathlib import Path

from configuration import FILTERS, ProjectFilters, KFile
from lib.find_kcl_files import find_kcl_files
from typing import Protocol, TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

class TestFunc(Protocol):
    def __call__(self, pf: ProjectFilters, kf: KFile, *args: Any, **kwargs: Any) -> Any: ...

Decorator: TypeAlias = Callable[[TestFunc], TestFunc]
TestCase: TypeAlias = Any  # pytest.param(...) is dynamically typed

def parametrize_kcl_files(
    *filters: ProjectFilters, print_debug: bool = False
) -> Decorator:
    def decorator(func: TestFunc) -> TestFunc:
        cases: list[TestCase] = []
        seen_paths: set[Path] = set()

        for pf in filters:
            filter_fn = FILTERS[pf]

            for kf in find_kcl_files(filter_fn=filter_fn, print_debug=print_debug):
                if kf.path in seen_paths:
                    continue
                seen_paths.add(kf.path)

                case_id = f"{pf.value}::{kf.path.stem}"
                cases.append(pytest.param(pf, kf, id=case_id))

        return pytest.mark.parametrize("pf, kf", cases)(func)

    return decorator
