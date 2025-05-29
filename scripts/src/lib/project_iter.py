from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict
from lib.helpers import find_project_root
import sys

from rich.panel import Panel
from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import (
    Progress,
    BarColumn,
    TimeElapsedColumn,
    TextColumn,
)

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

@dataclass
class KFile:
    path: Path
    dirname: DirEnum
    color: str

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
        root = PROJECT_ROOT.resolve()
    results: List[KFile] = []
    for file_path in root.rglob("*.k"):
        dirname = classify_path_closest(file_path)
        color_name = DIR_META.get(dirname, DIR_META[DirEnum.DEFAULT])
        kf = KFile(path=file_path, dirname=dirname, color=color_name)
        if filter_fn(kf):
            results.append(kf)
    return results

def run_callbacks_parallel(kfiles, callback, print_debug=True, title=None, hide_debug=False):
    console = Console()
    status_map = {kf.path: "[yellow]Pending" for kf in kfiles}
    panels = []

    def color_from_title(text):
        distinct_colors = [1, 2, 4, 5, 6, 11, 13, 14, 34, 82, 202, 226, 129, 45]
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        index = int(h, 16) % len(distinct_colors)
        return f"color({distinct_colors[index]})"

    def render_table():
        table = Table(show_lines=True)
        table.add_column("File")
        table.add_column("Type")
        table.add_column("Status")
        for kf in kfiles:
            path_str = str(kf.path.relative_to(PROJECT_ROOT))
            table.add_row(path_str, f"[{kf.color}]{kf.dirname.name}", status_map[kf.path])
        return table

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )
    task = progress.add_task("[cyan]Progress:", total=len(kfiles))

    # Group progress + table + panels (initially empty panels)
    def make_renderable():
        items = [progress, render_table()]
        if panels:
            items.extend(panels)
        group = Group(*items)
        table_color = color_from_title(title)
        return Panel(group, title=Text(title or "", style=f"bold {table_color}"), expand=True)

    with Live(make_renderable(), console=console, refresh_per_second=10) as live:
        for kf in kfiles:
            try:
                ret = callback(kf)
                if isinstance(ret, tuple):
                    result, extra_info = ret
                else:
                    result, extra_info = ret, None

                if not hide_debug and result:
                    panels.append(
                        Panel(
                            Text(result, style="white"),
                            title=f"[cyan]Result from {kf.path.name}",
                            border_style="cyan",
                            expand=True,
                        )
                    )
                if not hide_debug and extra_info:
                    panels.append(
                        Panel(
                            Syntax(extra_info, "text", theme="ansi_light", line_numbers=False, word_wrap=True),
                            title=f"[magenta]Extra Info from {kf.path.name}",
                            border_style="magenta",
                            expand=True,
                        )
                    )
                status_map[kf.path] = "[green]✔ Done"

            except Exception as e:
                from rich.traceback import Traceback
                tb = Traceback.from_exception(
                    type(e), e, e.__traceback__,
                    show_locals=False,
                    max_frames=1,
                    word_wrap=True,
                    theme="ansi_light",
                    indent_guides=True,
                )
                panels.append(
                    Panel(
                        tb,
                        title=f"[red]Exception in {kf.path.name}",
                        border_style="red",
                        expand=True,
                    )
                )
                status_map[kf.path] = "[red]✖ Error"
                live.update(make_renderable())
                sys.exit(1)

            progress.advance(task)
            live.update(make_renderable())

def process_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], Optional[str]]] = None,
    print_table: bool = True,
    title: Optional[str] = "",
    hide_debug: bool = True,
) -> List[KFile]:
    kfiles = find_kcl_files(root=root, filter_fn=filter_fn, print_debug=print_table)
    if callback:
        run_callbacks_parallel(kfiles, callback, print_debug=print_table, title=title, hide_debug=hide_debug)
        # add a few newlines between tests.
        print("\n")
    return kfiles
