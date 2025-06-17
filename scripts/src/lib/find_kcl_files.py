from collections.abc import Callable
from pathlib import Path
from configuration import KCL_ROOT, KFile


def find_kcl_files(
    root: Path | None = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
    glob_pattern: str | None = None,
) -> list[KFile]:
    if root is None:
        root = KCL_ROOT
    if glob_pattern is None:
        glob_pattern = "*.k"

    if print_debug:
        print(f"Scanning files in {root} with pattern '{glob_pattern}'")

    results: list[KFile] = []

    for file_path in root.rglob(glob_pattern):
        if not file_path.is_file():
            continue

        kf = KFile(path=file_path)

        if filter_fn(kf):
            results.append(kf)

    return results
