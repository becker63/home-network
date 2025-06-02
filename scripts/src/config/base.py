from pathlib import Path

from lib.find_proj_root import find_project_root

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()
