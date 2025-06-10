from configuration import ProjectFilters
from collections.abc import Callable
from typing import Any

def make_kcl_test(filter: ProjectFilters) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_kcl_filter", filter)
        return func
    return wrapper
