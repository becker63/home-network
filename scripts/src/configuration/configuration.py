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
CRD_ROOT = KCL_ROOT / "crds"
SCHEMA_ROOT = KCL_ROOT / "schemas"

# TODO: turn each of these version urls/strs into something more parsible, like a json file at the root so we can easily bump them
CRD_SPECS  = {
    "traefik": {
        "urls": [
            "https://raw.githubusercontent.com/traefik/traefik/refs/heads/v3.4/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml"
        ]
    },
    "kuttl": {
        "urls": [
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml",
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml",
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml"
        ]
    },
}

HELM_VALUES = {
    "oauth2-proxy": {
        "urls": [
            "https://raw.githubusercontent.com/oauth2-proxy/manifests/main/helm/oauth2-proxy/values.yaml"
        ]
    },
}

KCL_IMPORTS = {
    "external-secrets": "0.1.4",
    "argo-cd": "0.2.1",
    "fluxcd-helm-controller": "v1.0.3",
    "fluxcd": "0.1.2",
    "cert-manager": "0.3.0",
    "crossplane": "1.17.3",
    "fluxcd-source-controller": "v1.3.2",
    "crossplane-provider-gcp": "0.22.2",
}

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
