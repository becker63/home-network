from collections.abc import Callable
from pathlib import Path
from configuration import DirEnum, KFile

# In the past, we considered using full path structures to figure out
# which directory ("base", "proxy", etc.) a file belonged to.
#
# That approach required hardcoding folder paths like:
#   ["infra", "base", "proxy"] or ["schemas"]
#
# Instead, we now assume that every directory we care about (defined in DirEnum)
# has a **globally unique name** in the project.
#
# So if we see a directory called "proxy", we know it’s THE proxy.
# That lets us classify files based on name alone — no path logic needed.
#
# We enforce this at runtime by scanning for duplicates.

def classify_by_unique_dirname(path: Path) -> DirEnum:
    """
    Walks a file path from the deepest folder up,
    and returns the first folder that matches a known DirEnum (e.g., 'proxy', 'cluster').

    Because DirEnum names are unique, we don't need to check full folder paths.
    """
    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value.lower() == part.lower():
                return dir_enum
    return DirEnum.DEFAULT


def assert_unique_dirnames(root: Path, enums: list[DirEnum]) -> None:
    """
    Ensures that each DirEnum name appears only once across the entire project tree.

    This check guarantees that classification using folder names is unambiguous.
    If two folders are both named "proxy", this function will raise an error.
    """
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
    """
    Scans the project tree for files matching the pattern (default: '*.k').
    Classifies files based on their deepest matching folder (DirEnum),
    and returns only files (not directories) that pass the filter_fn.
    """
    from configuration import KCL_ROOT, DirEnum  # avoid circular import

    if root is None:
        root = KCL_ROOT
    if glob_pattern is None:
        glob_pattern = "*.k"

    # Enforce unique folder names (e.g. only one 'proxy', 'base', etc.)
    assert_unique_dirnames(root, list(DirEnum))

    if print_debug:
        print(f"Scanning files in {root} with pattern '{glob_pattern}'")

    results: list[KFile] = []

    for file_path in root.rglob(glob_pattern):
        if not file_path.is_file():
            continue  # 🚫 Skip directories and symlinks

        dirname = classify_by_unique_dirname(file_path)
        kf = KFile(path=file_path, dirname=dirname)

        if filter_fn(kf):
            results.append(kf)

    return results
