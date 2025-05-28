from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict, Literal
from colored import fg, attr
from lib.helpers import find_project_root
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

ColorName = Literal["blue", "green", "magenta", "grey_50"]

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

DIR_META: Dict[DirEnum, ColorName] = {
    DirEnum.BOOTSTRAP: "blue",
    DirEnum.FRP_SCHEMA: "green",
    DirEnum.SCHEMAS: "magenta",
    DirEnum.DEFAULT: "grey_50",
}

def classify_path_closest(path: Path) -> DirEnum:
    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value == part:
                return dir_enum
    return DirEnum.DEFAULT

@dataclass
class KFile:
    path: Path
    dirname: DirEnum
    color: ColorName

def find_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
) -> List[KFile]:
    if root is None:
        root = (find_project_root() / "infra").resolve()
    if print_debug:
        print(f"Scanning KCL files in {root}")

    results: List[KFile] = []

    for file_path in root.rglob("*.k"):
        dirname = classify_path_closest(file_path)
        color_name = DIR_META.get(dirname, DIR_META[DirEnum.DEFAULT])
        kf = KFile(path=file_path, dirname=dirname, color=color_name)

        if filter_fn(kf):
            results.append(kf)

    return results

def run_callbacks_parallel(
    kfiles: List[KFile],
    callback: Callable[[KFile], None],
    print_debug: bool = True,
) -> None:
    def _wrapper(kf: KFile):
        relative_path = kf.path.relative_to(find_project_root() / "infra")
        print(f"Processing: {fg(kf.color)}{relative_path} [folder: {kf.dirname.name}]{attr('reset')}")
        callback(kf)

    max_workers = min(32, (os.cpu_count() or 1) + 4)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_wrapper, kf): kf for kf in kfiles}

        for future in as_completed(futures):
            kf = futures[future]
            try:
                future.result()
                if print_debug:
                    relative_path = kf.path.relative_to(find_project_root() / "infra")
                    print(f"Completed: {fg(kf.color)}{relative_path}{attr('reset')}")
            except Exception as e:
                print(f"Error processing {kf.path}: {e}")

def process_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], None]] = None,
    print_debug: bool = True,
) -> List[KFile]:
    kfiles = find_kcl_files(root=root, filter_fn=filter_fn, print_debug=print_debug)
    if callback:
        run_callbacks_parallel(kfiles, callback, print_debug=print_debug)
    return kfiles
