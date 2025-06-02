from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only import for type checking (no runtime import)
    from config.schema import DirEnum

@dataclass
class KFile:
    path: Path
    dirname: 'DirEnum'  # forward ref as string
