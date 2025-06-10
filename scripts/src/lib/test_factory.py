from configuration import ProjectFilters
from collections.abc import Callable
from typing import Any

def make_kcl_test(filter: ProjectFilters) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory that tags a test function with a ProjectFilters value.

    This works with pytest's `pytest_generate_tests` hook inside conftest, which runs for each test function.

    Pytest gives us a `Metafunc` object that includes `metafunc.function` — the actual
    decorated test function. We attach `_kcl_filter` to that function so the hook
    can detect and parameterize it.

    The type `Callable[..., Any]` is used to generically represent any test function,
    regardless of its argument signature. This keeps the decorator compatible with all
    pytest tests without needing to know their exact parameter types.

    This removes the need to repeat boilerplate like:

        @pytest.mark.parametrize(
            "pf, kf",
            filter_kcl_files(all_kcl_files, ProjectFilters.BASE)
        )
        def test_something(pf, kf): ...

    Instead, you can write:

        @make_kcl_test(ProjectFilters.BASE)
        def test_something(pf, kf): ...

    Cleaner, more declarative, and centralizes test configuration.
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        func._kcl_filter = filter  # type: ignore[attr-defined]
        return func

    return wrapper
