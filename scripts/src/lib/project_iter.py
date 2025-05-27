from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict, Literal
from colored import fg, attr

# Colored doesnt have super great types
ColorName = Literal["blue", "green", "magenta", "grey_50"]

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP = "frp"
    SCHEMAS = "schemas"
    DEFAULT = "default"

# if I cared more we could make this more dry prob
# Oh well..
DIR_META: Dict[DirEnum, ColorName] = {
    DirEnum.BOOTSTRAP: "blue",
    DirEnum.FRP: "green",
    DirEnum.SCHEMAS: "magenta",
    DirEnum.DEFAULT: "grey_50",
}

def classify_path(path: Path) -> DirEnum:
    for part in path.parts:
        for dir_enum in DirEnum:
            if dir_enum.value == part:
                return dir_enum
    return DirEnum.DEFAULT

@dataclass
class KFile:
    path: Path
    dirname: DirEnum
    color: ColorName

def project_filter_enum(
    root: str = "infra",
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], None]] = None,
    print_debug: bool = True
) -> List[KFile]:
    results: List[KFile] = []

    for file_path in Path(root).rglob("*.k"):
        dir_enum = classify_path(file_path)
        color_name = DIR_META.get(dir_enum, DIR_META[DirEnum.DEFAULT])
        kf = KFile(path=file_path, dirname=dir_enum, color=color_name)

        if filter_fn(kf):
            if print_debug:
                print(f"{fg(kf.color)}Processing: {kf.path} [folder: {kf.dirname.name}]{attr('reset')}")
            results.append(kf)
            if callback:
                callback(kf)

    return results
