from collections.abc import Callable
from pathlib import Path
from configuration import KCL_ROOT, KFile
from lib.debug import debug_print


def find_kcl_files(
    root: Path | None = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool | None = None,  # Still here for compatibility
    glob_pattern: str | None = None,
) -> list[KFile]:
    # Fall back to debug flag if not passed explicitly
    if root is None:
        root = KCL_ROOT
    if glob_pattern is None:
        glob_pattern = "*.k"

    debug_print(f"[DEBUG] Scanning files in {root} with pattern '{glob_pattern}'")

    results: list[KFile] = []

    for file_path in root.rglob(glob_pattern):
        if not file_path.is_file():
            continue

        kf = KFile(path=file_path)

        if filter_fn(kf):
            debug_print(f"[DEBUG]  ✓ Matched file: {file_path}")
            results.append(kf)

    return results
