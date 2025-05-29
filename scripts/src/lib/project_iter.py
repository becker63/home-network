from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict
from lib.helpers import find_project_root
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import hashlib

from rich.console import Group
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TextColumn

class DirEnum(Enum):
    BOOTSTRAP = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS = "schemas"
    DEFAULT = "default"

DIR_META: Dict[DirEnum, str] = {
    DirEnum.BOOTSTRAP: "blue",
    DirEnum.FRP_SCHEMA: "green",
    DirEnum.SCHEMAS: "magenta",
    DirEnum.DEFAULT: "grey_50",
}

PROJECT_ROOT = find_project_root() / "kcl"

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
    color: str

def find_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    print_debug: bool = True,
) -> List[KFile]:
    if root is None:
        root = PROJECT_ROOT.resolve()

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
    title: Optional[str] = "KCL File Processing Status",
) -> None:
    status_map = {kf.path: "[yellow]Pending" for kf in kfiles}

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )

    task_id = progress.add_task("Processing KCL files", total=len(kfiles))

    def color_from_title(text: str) -> str:
        # Distinct colors according to gpt
        distinct_colors = [1,2,4,5,6,11,13,14,34,82,202,226,129,45]
        h = hashlib.md5(text.encode()).hexdigest()
        index = int(h, 16) % len(distinct_colors)
        return f"color({distinct_colors[index]})"

    def render_table():
        actual_title = title or ""
        table_color = color_from_title(actual_title)
        table = Table(title=Text(actual_title, style=f"bold {table_color}"), show_lines=True)
        table.add_column("File")
        table.add_column("Type")
        table.add_column("Status")
        for kf in kfiles:
            path_str = str(kf.path.relative_to(PROJECT_ROOT))
            table.add_row(path_str, f"[{kf.color}]{kf.dirname.name}", status_map[kf.path])
        return table

    def _wrapped_callback(kf: KFile):
        try:
            callback(kf)
            status_map[kf.path] = "[green]✔ Done"
        except Exception as e:
            status_map[kf.path] = f"[red]✖ Error: {e}"
        progress.update(task_id, advance=1)

    max_workers = min(32, (os.cpu_count() or 1) + 4)

    print("\n")
    with Live(Group(render_table(), progress), refresh_per_second=10) as live:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_wrapped_callback, kf): kf for kf in kfiles}
            for _ in as_completed(futures):
                live.update(Group(render_table(), progress))
    print("\n")

def process_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], None]] = None,
    print_table: bool = True,
    title: Optional[str] = "KCL File Processing Status",
) -> List[KFile]:
    kfiles = find_kcl_files(root=root, filter_fn=filter_fn, print_debug=print_table)
    if callback:
        run_callbacks_parallel(kfiles, callback, print_debug=print_table, title=title)
    return kfiles
