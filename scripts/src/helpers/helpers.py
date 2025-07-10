import subprocess
import socket

def get_free_port() -> int:
    """Bind to port 0 to let the OS choose a free port, then close and return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class CommandError(Exception):
    def __init__(self, extra_info: str | None = None):
        super().__init__()
        self.__rich_info__ = extra_info

    def __str__(self) -> str:
        return "your command broke dawg"

def run_command(cmd: list[str], kf_name: str | None = None) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise CommandError(
            extra_info=e.stderr.strip() or e.stdout.strip() or "No stderr or stdout output"
        ) from e

import shutil
from pathlib import Path

def remove_path(p: Path):
    if not p.exists():
        return

    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
