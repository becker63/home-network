from typing import Callable, Optional, List
from pathlib import Path
from .common import DirEnum, KFile
from .helpers import find_project_root

def classify_path_closest(path: Path) -> DirEnum:
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
    if root is None:
        root = (find_project_root() / "kcl").resolve()
    if print_debug:
        print(f"Scanning KCL files in {root}")

    results: List[KFile] = []

    for file_path in root.rglob("*.k"):
        dirname = classify_path_closest(file_path)
        kf = KFile(path=file_path, dirname=dirname)

        if filter_fn(kf):
            results.append(kf)

    return results
