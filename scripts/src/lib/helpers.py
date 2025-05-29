from pathlib import Path
from typing import Optional
import subprocess
from typing import List, Optional

def find_project_root() -> Path:
    current = Path(__file__).resolve()
    markers = ["flake.nix", ".git"]

    while True:
        if any((current / marker).exists() for marker in markers):
            return current
        if current.parent == current:
            raise RuntimeError(f"Could not find project root. Missing any of: {markers}")
        current = current.parent

class CommandError(Exception):
    def __init__(self, extra_info: Optional[str] = None):
        super().__init__()
        self.__rich_info__ = extra_info

    def __str__(self) -> str:
        return "your command broke dawg"

def run_command(cmd: List[str], kf_name: Optional[str] = None) -> str:
    """Run a shell command and return stdout, raising CommandError on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Use e.stderr, e.stdout directly from exception object
        raise CommandError(
            extra_info=e.stderr.strip() or e.stdout.strip() or "No stderr or stdout output"
        ) from e
