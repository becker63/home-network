# src/lib/find_kcl_files.py

from typing import Callable, Optional, List
from pathlib import Path

from lib.proj_types import KFile

def classify_path_closest(path: Path):
    # We do a lazy import here to avoid circular‐import problems
    from project_config import DirEnum

    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value == part:
                return dir_enum
    return DirEnum.DEFAULT

def find_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
) -> List[KFile]:
    # Lazy import to avoid circular import
    from project_config import KCL_ROOT

    if root is None:
        root = KCL_ROOT
    if print_debug:
        print(f"Scanning KCL files in {root}")

    results: List[KFile] = []
    for file_path in root.rglob("*.k"):
        dirname = classify_path_closest(file_path)
        kf = KFile(path=file_path, dirname=dirname)
        if filter_fn(kf):
            results.append(kf)
    return results
