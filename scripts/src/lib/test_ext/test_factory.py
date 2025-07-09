from typing import TypeVar, Callable, ParamSpec
from configuration import KFile


F = TypeVar("F", bound=Callable[..., object])

def make_kcl_test(filter_fn: Callable[[KFile], bool]) -> Callable[[F], F]:
    def decorator(test_func: F) -> F:
        test_func._kcl_filter_fn = filter_fn  # type: ignore[attr-defined]
        return test_func
    return decorator

P = ParamSpec("P")

def make_kcl_group_test(
    filenames: list[str],
    filter_fn: Callable[[KFile], bool],
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, "_kcl_group_filenames", filenames)
        setattr(func, "_kcl_group_filter", filter_fn)
        return func
    return decorator
