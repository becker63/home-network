import json
from pathlib import Path
from typing import List

from .models import RemoteSchema
from .configuration import PROJECT_ROOT


CRD_SPEC_PATH = PROJECT_ROOT / "crds.json"


def load_crd_specs(path: Path = CRD_SPEC_PATH) -> List[RemoteSchema]:
    with path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
    loaded = [RemoteSchema.model_validate(item) for item in raw_data]
    return loaded


# --- Loaded CRD specs ---
CRD_SPECS = load_crd_specs()
