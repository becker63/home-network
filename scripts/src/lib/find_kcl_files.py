from collections.abc import Callable
from pathlib import Path

from configuration import DirEnum, KFile


def classify_path_by_top_level(path: Path) -> DirEnum:
    """
    Classify based on the top-level folder immediately under KCL_ROOT.
    e.g. kcl/infra/base/cluster/file.kcl → DirEnum.INFRA
    """
    from configuration import KCL_ROOT

    try:
        relative = path.relative_to(KCL_ROOT)
    except ValueError:
        return DirEnum.DEFAULT  # Not under KCL_ROOT

    top_level = relative.parts[0] if relative.parts else ""
    for dir_enum in DirEnum:
        if dir_enum.value.lower() == top_level.lower():
            return dir_enum

    return DirEnum.DEFAULT


def find_kcl_files(
    root: Path | None = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
) -> list[KFile]:
    from configuration import KCL_ROOT  # Lazy import to avoid circular ref

    if root is None:
        root = KCL_ROOT
    if print_debug:
        print(f"Scanning KCL files in {root}")

    results: list[KFile] = []

    # Always recurse into subdirectories and pick *.kcl files
    for file_path in root.rglob("*"):
        dirname = classify_path_by_top_level(file_path)
        kf = KFile(path=file_path, dirname=dirname)
        if filter_fn(kf):
            results.append(kf)

    return results
