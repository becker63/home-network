from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Callable, Optional, List, Dict
from lib.helpers import find_project_root
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import hashlib
import traceback
import re
from io import StringIO
import sys

from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TextColumn,
)

# Enums and Metadata
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

# Data Class
@dataclass
class KFile:
    path: Path
    dirname: DirEnum
    color: str

# Utility Functions
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

def clean_traceback(tb_text: str) -> str:
    tb_text = re.sub(r"/nix/store/[a-z0-9]+-[^/\s]+/bin/", "", tb_text)
    home_dir = os.path.expanduser("~") + "/home-network/scripts/src/"
    tb_text = tb_text.replace(home_dir, "")
    return tb_text

# Parallel Execution
def run_callbacks_parallel(
    kfiles: List[KFile],
    callback: Callable[[KFile], Optional[str]],
    print_debug: bool = True,
    title: Optional[str] = "KCL File Processing Status",
) -> None:
    console = Console()
    status_map = {kf.path: "[yellow]Pending" for kf in kfiles}
    panels: List = []

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
        distinct_colors = [1, 2, 4, 5, 6, 11, 13, 14, 34, 82, 202, 226, 129, 45]
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
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        raw_out = StringIO()
        raw_err = StringIO()

        try:
            # Redirect stdout and stderr to StringIO buffers
            sys.stdout = raw_out
            sys.stderr = raw_err

            with console.capture() as capture:
                result = callback(kf)

            # Restore original stdout and stderr immediately after callback returns
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

            rich_output = capture.get()
            raw_output = raw_out.getvalue()
            raw_error = raw_err.getvalue()

            combined_output = ""
            if rich_output.strip():
                combined_output += rich_output.strip()
            if raw_output.strip():
                if combined_output:
                    combined_output += "\n\n"
                combined_output += raw_output.strip()
            if raw_error.strip():
                if combined_output:
                    combined_output += "\n\n"
                combined_output += f"STDERR:\n{raw_error.strip()}"

            panels.append(Text())
            panels.append(
                Panel(
                    Syntax(combined_output or "<no output>", "bash", theme="ansi_light", word_wrap=True),
                    title=f"[bold blue]{kf.path.relative_to(PROJECT_ROOT)}",
                    expand=True,
                )
            )
            status_map[kf.path] = "[green]✔ Done"

        except Exception as e:
            # Make sure to restore stdout/stderr if error happens
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

            tb_lines = traceback.format_exception(type(e), e, e.__traceback__, chain=True)
            tb_text = ''.join(tb_lines)
            cleaned_tb = clean_traceback(tb_text)
            panels.append(Text())
            panels.append(
                Panel(
                    Syntax(cleaned_tb, "python", theme="ansi_light", line_numbers=True, word_wrap=True),
                    title=f"[red]Exception in {kf.path.name}",
                    expand=True,
                )
            )
            status_map[kf.path] = "[red]✖ Error"
        progress.update(task_id, advance=1)

    max_workers = min(32, (os.cpu_count() or 1) + 4)

    print("\n")
    with Live(refresh_per_second=10) as live:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_wrapped_callback, kf): kf for kf in kfiles}
            for _ in as_completed(futures):
                all_panels = [Text()] + [Group(panel, Text()) for panel in panels]
                live.update(Group(render_table(), progress, *all_panels))
    print("\n")

# Public Entry
def process_kcl_files(
    root: Optional[Path] = None,
    filter_fn: Callable[[KFile], bool] = lambda kf: True,
    callback: Optional[Callable[[KFile], Optional[str]]] = None,
    print_table: bool = True,
    title: Optional[str] = "KCL File Processing Status",
) -> List[KFile]:
    kfiles = find_kcl_files(root=root, filter_fn=filter_fn, print_debug=print_table)
    if callback:
        run_callbacks_parallel(kfiles, callback, print_debug=print_table, title=title)
    return kfiles
