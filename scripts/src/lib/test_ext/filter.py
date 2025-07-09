from typing import Any, TypeAlias

from configuration import KFile

TestCase: TypeAlias = Any  # pytest.param(...)


from collections.abc import Callable

def filter_kcl_files(
    kcl_files: list[KFile],
    filter_fn: Callable[[KFile], bool]
) -> list[tuple[KFile, KFile]]:
    return [
        (pf, kf)
        for pf in kcl_files
        for kf in kcl_files
        if filter_fn(kf)
    ]
