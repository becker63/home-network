from typing import Any
from typing import TypeVar, Callable
from configuration import KFile


F = TypeVar("F", bound=Callable[..., object])

def make_kcl_test(filter_fn: Callable[[KFile], bool]) -> Callable[[F], F]:
    def decorator(test_func: F) -> F:
        test_func._kcl_filter_fn = filter_fn  # type: ignore[attr-defined]
        return test_func
    return decorator


def make_kcl_group_test(path_substrs: list[str], group_filter: Callable[[Any], bool]) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, "_kcl_group_substrs", path_substrs)
        setattr(func, "_kcl_group_filter", group_filter)
        return func
    return decorator
