from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only import for type checking (no runtime import)
    from project_config import ProjectConfig

@dataclass
class KFile:
    path: Path
    dirname: 'ProjectConfig.DirEnum'  # forward ref as string
