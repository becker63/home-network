from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict, Literal
from colored import fg, attr
from lib.helpers import find_project_root

# Colored doesn't have super great types
ColorName = Literal["blue", "green", "magenta", "grey_50"]

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

# Color map for folders
DIR_META: Dict[DirEnum, ColorName] = {
    DirEnum.BOOTSTRAP: "blue",
    DirEnum.FRP_SCHEMA: "green",
    DirEnum.SCHEMAS: "magenta",
    DirEnum.DEFAULT: "grey_50",
}

def classify_path_closest(path: Path) -> DirEnum:
    # Search from the file's folder upward to root — closest folder match
    for part in reversed(path.parts):
        for dir_enum in DirEnum:
            if dir_enum.value == part:
                return dir_enum
    return DirEnum.DEFAULT

@dataclass
class KFile:
    path: Path
    dirname: DirEnum  # closest folder classification
    color: ColorName

def project_filter_enum(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], None]] = None,
    print_debug: bool = True
) -> List[KFile]:
    if root is None:
        root = (find_project_root() / "infra").resolve()
    print(root)

    results: List[KFile] = []

    for file_path in root.rglob("*.k"):
        dirname = classify_path_closest(file_path)  # closest folder for both label & color
        color_name = DIR_META.get(dirname, DIR_META[DirEnum.DEFAULT])
        kf = KFile(path=file_path, dirname=dirname, color=color_name)

        if filter_fn(kf):
            relative_path = kf.path.relative_to(root)
            if print_debug:
                print(f"Processing: {fg(kf.color)}{relative_path} [folder: {kf.dirname.name}]{attr('reset')}")
            results.append(kf)
            if callback:
                callback(kf)

    return results
