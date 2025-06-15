from enum import StrEnum, auto
from pathlib import Path
from typing import Callable
from pydantic import BaseModel, ConfigDict
from lib.find_proj_root import find_project_root

class DirEnum(StrEnum):
    CLUSTER = "cluster"
    PROXY = "proxy"
    SCHEMAS = "schemas"
    INFRA = "infra"
    DEFAULT = "default"
    BASE = "base"
    HELM= "helmreleases"


class ProjectFilters(StrEnum):
    BASE = auto()
    PROXY_E2E = auto()
    PROXY_TEST = auto()
    RANDOM = auto()
    DEFAULT = auto()
    INFRA_KCL = auto()
    INFRA_NIX = auto()
    CLUSTER = auto()
    HELM = auto()


class KFile(BaseModel):
    path: Path
    dirname: DirEnum

    model_config = ConfigDict(frozen=True)


PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "kcl").resolve()


FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    # Matches nested files in the base folder
    ProjectFilters.BASE: lambda kf: (
        DirEnum.BASE.value in kf.path.parts
    ),

    # Matches files classified as 'proxy'
    ProjectFilters.PROXY_TEST: lambda kf: (
        kf.dirname == DirEnum.PROXY
    ),

    # Matches files in 'proxy' or specifically frpc_daemonset.k in 'cluster'
    ProjectFilters.PROXY_E2E: lambda kf: (
        kf.dirname == DirEnum.PROXY
        or (kf.dirname == DirEnum.CLUSTER and "frpc_daemonset" in kf.path.name)
    ),

    # Matches files under the 'infra' folder, classified by folder name
    ProjectFilters.INFRA_KCL: lambda kf: (
        DirEnum.INFRA.value in kf.path.parts
    ),

    # everything inside cluster, mostly for yaml synth
    ProjectFilters.CLUSTER: lambda kf: (
        DirEnum.CLUSTER.value in kf.path.parts
    ),

    ProjectFilters.HELM: lambda kf: (
        DirEnum.HELM.value in kf.path.parts
    ),

    # Catch-all for all files scanned
    ProjectFilters.DEFAULT: lambda kf: True,
}
