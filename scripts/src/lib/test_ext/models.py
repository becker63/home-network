from pydantic import BaseModel, Field
from typing import Callable, List, Optional

from configuration import KFile


class KCLTestMetadata(BaseModel):
    all_files: List[KFile] = Field(default_factory=list)
    group_filenames: Optional[List[str]] = None
    group_filter: Optional[Callable[[KFile], bool]] = None
    file_filter: Optional[Callable[[KFile], bool]] = None

    class Config:
        arbitrary_types_allowed = True  # Allow KFile and Callable
