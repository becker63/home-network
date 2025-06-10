from collections.abc import Callable
from pathlib import Path
from configuration import DirEnum, KFile

def classify_by_unique_dirname(path: Path) -> DirEnum:
    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value.lower() == part.lower():
                return dir_enum
    return DirEnum.DEFAULT

def assert_unique_dirnames(root: Path, enums: list[DirEnum]) -> None:
    seen: dict[str, Path] = {}
    for dir_path in root.rglob("*"):
        if not dir_path.is_dir():
            continue
        name = dir_path.name.lower()
        for enum in enums:
            if name == enum.value.lower():
                if name in seen:
                    raise RuntimeError(
                        f"DirEnum name conflict: '{name}' found in both {seen[name]} and {dir_path}"
                    )
                seen[name] = dir_path

def find_kcl_files(
    root: Path | None = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
    glob_pattern: str | None = None,
) -> list[KFile]:
    from configuration import KCL_ROOT, DirEnum  # avoid circular import

    if root is None:
        root = KCL_ROOT
    if glob_pattern is None:
        glob_pattern = "*.k"

    assert_unique_dirnames(root, list(DirEnum))

    if print_debug:
        print(f"Scanning files in {root} with pattern '{glob_pattern}'")

    results: list[KFile] = []

    for file_path in root.rglob(glob_pattern):
        if not file_path.is_file():
            continue

        dirname = classify_by_unique_dirname(file_path)
        kf = KFile(path=file_path, dirname=dirname)

        if filter_fn(kf):
            results.append(kf)

    return results
