# configuration/models.py

from pathlib import Path
from typing import List
from pydantic import BaseModel, ConfigDict


class KFile(BaseModel):
    path: Path
    model_config = ConfigDict(frozen=True)


class RemoteSchema(BaseModel):
    name: str
    urls: List[str]
    model_config = ConfigDict(frozen=True)
