from pathlib import Path
from typing import Optional, List
import subprocess

from kcl_lib import api
from kcl_lib.api import ExecProgram_Args

from .proj_types import KFile

def find_project_root() -> Path:
    current = Path(__file__).resolve()
    while True:
        if (current / "flake.nix").exists():
            return current
        if current.parent == current:
            raise RuntimeError("Could not find project root (missing flake.nix)")
        current = current.parent

KCL_ROOT: Path = (find_project_root() / "kcl").resolve()

class CommandError(Exception):
    def __init__(self, extra_info: Optional[str] = None):
        super().__init__()
        self.__rich_info__ = extra_info

    def __str__(self) -> str:
        return "your command broke dawg"

def run_command(cmd: List[str], kf_name: Optional[str] = None) -> str:
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
