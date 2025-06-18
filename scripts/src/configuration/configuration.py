from enum import StrEnum, auto
from pathlib import Path
from typing import Callable
from pydantic import BaseModel, ConfigDict
from lib.find_proj_root import find_project_root


# --- Project filter modes (used in tests/build steps/etc.) ---
class ProjectFilters(StrEnum):
    BASE = auto()
    PROXY_E2E = auto()
    PROXY_TEST = auto()
    CONTROL = auto()
    WORK = auto()
    INGRESS = auto()
    META = auto()
    INFRA_KCL = auto()
    HELM = auto()
    DEFAULT = auto()


# --- KCL file abstraction ---
class KFile(BaseModel):
    path: Path
    model_config = ConfigDict(frozen=True)


# --- Paths ---
PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "configurations").resolve()
CRD_ROOT = KCL_ROOT / "crds"
SCHEMA_ROOT = KCL_ROOT / "schemas"


# --- Filter logic ---
FILTERS: dict[ProjectFilters, Callable[[KFile], bool]] = {
    ProjectFilters.BASE: lambda kf: "base" in kf.path.parts,

    ProjectFilters.PROXY_TEST: lambda kf: (
        "infra" in kf.path.parts
        and "base" in kf.path.parts
        and kf.path.name in {"FRPC_Config.k", "FRPS_Config.k"}
    ),

    ProjectFilters.PROXY_E2E: lambda kf: (
        (
            "infra" in kf.path.parts
            and "base" in kf.path.parts
            and (
                kf.path.name in {"FRPC_Config.k", "frpc_daemonset.k", "FRPS_Config.k"}
            )
        )
    ),

    ProjectFilters.CONTROL: lambda kf: (
        "control" in kf.path.parts and kf.path.suffix == ".k"
    ),

    ProjectFilters.WORK: lambda kf: kf.path.match("**/work/**/*.k"),

    ProjectFilters.INGRESS: lambda kf: "ingress" in kf.path.parts,

    ProjectFilters.META: lambda kf: (
        (PROJECT_ROOT / "kcl" / "infra" / "meta") in kf.path.parents
    ),

    ProjectFilters.INFRA_KCL: lambda kf: "infra" in kf.path.parts,

    ProjectFilters.HELM: lambda kf: "helmreleases" in kf.path.parts,

    ProjectFilters.DEFAULT: lambda kf: True,
}


# --- Version and import tracking ---
CRD_SPECS = {
    "traefik": {
        "urls": [
            "https://raw.githubusercontent.com/traefik/traefik/refs/heads/v3.4/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml"
        ]
    },
    "infisical_operator": {
        "urls": [
            "https://raw.githubusercontent.com/Infisical/infisical/refs/heads/main/k8-operator/config/crd/bases/secrets.infisical.com_infisicalsecrets.yaml"
        ]
    },
    "crossplane_composistion": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane/crossplane/refs/tags/v1.17.1/cluster/crds/apiextensions.crossplane.io_compositions.yaml"
        ]
    },
    "crossplane_patch_and_transform": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane-contrib/function-patch-and-transform/refs/heads/main/package/input/pt.fn.crossplane.io_resources.yaml"
        ]
    },
    "crossplane_sequencer": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane-contrib/function-sequencer/refs/heads/main/package/input/sequencer.fn.crossplane.io_inputs.yaml"
        ]
    },
    "crossplane_nop": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane-contrib/provider-nop/refs/heads/main/package/crds/nop.crossplane.io_nopresources.yaml"
        ]
    }
}

HELM_VALUES = {
    "oauth2-proxy": {
        "urls": [
            "https://raw.githubusercontent.com/oauth2-proxy/manifests/main/helm/oauth2-proxy/values.yaml"
        ]
    },
}

KCL_IMPORTS = {
    "cert-manager": "0.3.0",
    "crossplane": "1.17.3",
    "fluxcd-helm-controller": "v1.0.3",
    "fluxcd-source-controller": "v1.3.2",
    "crossplane-provider-upjet-gcp": "1.0.5",
    "fluxcd": "0.1.2",
}
