from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict, Literal
from colored import fg, attr
from lib.helpers import find_project_root

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
