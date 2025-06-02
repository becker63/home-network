#!/bin/bash

set -e

echo "Creating config/ directory..."
mkdir -p config

echo "Backing up original project_config.py..."
cp project_config.py project_config.py.bak

echo "Writing config/schema.py..."
cat > config/schema.py <<EOF
from enum import Enum, StrEnum
from pathlib import Path
from dataclasses import dataclass

class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

@dataclass(frozen=True)
class KFile:
    path: Path
    dirname: DirEnum
EOF

echo "Writing config/base.py..."
cat > config/base.py <<EOF
from pathlib import Path
from lib.find_proj_root import find_project_root

PROJECT_ROOT: Path = find_project_root()
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()
EOF

echo "Writing config/filters.py..."
cat > config/filters.py <<EOF
from typing import Callable, Dict
from config.schema import KFile, ProjectFilters, DirEnum

FILTERS: Dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
    ProjectFilters.RANDOM:           lambda _kf: True,
}
EOF

echo "Updating imports across the codebase..."

find . -type f -name "*.py" -exec sed -i \
    -e 's/from project_config import DirEnum/from config.schema import DirEnum/g' \
    -e 's/from project_config import ProjectFilters/from config.schema import ProjectFilters/g' \
    -e 's/from project_config import KFile/from config.schema import KFile/g' \
    -e 's/from project_config import PROJECT_ROOT/from config.base import PROJECT_ROOT/g' \
    -e 's/from project_config import KCL_ROOT/from config.base import KCL_ROOT/g' \
    -e 's/from project_config import FILTERS/from config.filters import FILTERS/g' \
    {} +

echo "Refactor complete ✅"
echo "You can now delete project_config.py if everything works."
