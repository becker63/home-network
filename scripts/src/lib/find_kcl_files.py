from collections.abc import Callable
from pathlib import Path
from configuration import DirEnum, KFile

def classify_path_closest(path: Path) -> DirEnum:
    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value.lower() == part.lower():
                return dir_enum
    return DirEnum.DEFAULT

def find_kcl_files(
    root: Path | None = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
    glob_pattern: str | None = None,  # 👈 Optional pattern
) -> list[KFile]:
    from configuration import KCL_ROOT  # Lazy import to avoid circular ref

    if root is None:
        root = KCL_ROOT
    if glob_pattern is None:
        glob_pattern = "*.k"

    if print_debug:
        print(f"Scanning files in {root} with pattern '{glob_pattern}'")

    results: list[KFile] = []

    for file_path in root.rglob(glob_pattern):
        dirname = classify_path_closest(file_path)
        kf = KFile(path=file_path, dirname=dirname)
        if filter_fn(kf):
            results.append(kf)

    return results
