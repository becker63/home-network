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


class ProjectFilters(StrEnum):
    BASE = auto()
    PROXY_E2E = auto()
    PROXY_TEST = auto()
    RANDOM = auto()
    DEFAULT = auto()
    INFRA_KCL = auto()
    INFRA_NIX = auto()


class KFile(BaseModel):
    path: Path
    dirname: DirEnum

    model_config = ConfigDict(frozen=True)


PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "kcl").resolve()


FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    # Matches files in the cluster directory, only if they are .k files
    ProjectFilters.BASE: lambda kf: (
        kf.dirname == DirEnum.CLUSTER and kf.path.suffix == ".k"
    ),

    # Matches .k files in the proxy directory
    ProjectFilters.PROXY_TEST: lambda kf: (
        kf.dirname == DirEnum.PROXY and kf.path.suffix == ".k"
    ),

    # Matches .k files in proxy OR cluster/frpc_daemonset specifically
    ProjectFilters.PROXY_E2E: lambda kf: (
        kf.path.suffix == ".k"
        and (
            kf.dirname == DirEnum.PROXY
            or (kf.dirname == DirEnum.CLUSTER and "frpc_daemonset" in kf.path.name)
        )
    ),

    # Every kcl file under the infra folder,
    # (I'm not sure why we need to use kf.path.parents or KCL_ROOT —
    # we need to look at our classifier under find_kcl_files I think)
    ProjectFilters.INFRA_KCL: lambda kf: (
        kf.path.suffix == ".k"
        and (KCL_ROOT / DirEnum.INFRA) in kf.path.parents
    ),

    # Every file under the kcl dir, including schemas and dirs
    ProjectFilters.DEFAULT: lambda kf: True,
}
