# lib/config_loader.py
import tomllib
from pathlib import Path
from typing import Any


def find_pyproject(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()
    for parent in [start, *start.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Could not find pyproject.toml starting from: " + str(start))


def load_kcltest_debug_flag() -> bool:
    path = find_pyproject()
    with path.open("rb") as f:
        config = tomllib.load(f)
    return config.get("tool", {}).get("kcltest_config", {}).get("debug", False)

def debug_print(*args: Any, **kwargs: Any) -> None:
    if load_kcltest_debug_flag():
        print(*args, **kwargs)
