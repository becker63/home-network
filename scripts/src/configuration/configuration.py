from enum import StrEnum, auto
from pathlib import Path
from typing import Callable
from pydantic import BaseModel, ConfigDict
from lib.test_ext.find_proj_root import find_project_root


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
    CLEANUP_TEST = auto()


# --- KCL file abstraction ---
class KFile(BaseModel):
    path: Path
    model_config = ConfigDict(frozen=True)


# --- Paths ---
PROJECT_ROOT = find_project_root()
KCL_ROOT = (PROJECT_ROOT / "configurations").resolve()
CRD_ROOT = KCL_ROOT / "crds"
SCHEMA_ROOT = PROJECT_ROOT / "kcl_common" / "schemas"


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

    ProjectFilters.CLEANUP_TEST: lambda kf: (
        "managed_frps" in kf.path.parts and
        "control" in kf.path.parts and
        kf.path.name == "test_function.k"
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
    "digitalocean": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/digitalocean.crossplane.io_providerconfigs.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/droplet.digitalocean.crossplane.io_droplets.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/dns.digitalocean.crossplane.io_domains.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/dns.digitalocean.crossplane.io_records.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/networking.digitalocean.crossplane.io_ipassignments.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/networking.digitalocean.crossplane.io_ips.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/project.digitalocean.crossplane.io_projects.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/uptime.digitalocean.crossplane.io_alerts.yaml",
            "https://raw.githubusercontent.com/crossplane-contrib/provider-upjet-digitalocean/refs/heads/main/package/crds/custom.digitalocean.crossplane.io_images.yaml"
        ]
    },
    "crossplane_kcl_function": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane-contrib/function-kcl/refs/heads/main/package/input/template.fn.crossplane.io_kclinputs.yaml"
        ]
    },
    "fluxcd_kustomize_controller": {
        "urls": [
            "https://raw.githubusercontent.com/fluxcd/kustomize-controller/refs/heads/main/config/crd/bases/kustomize.toolkit.fluxcd.io_kustomizations.yaml"
        ]
    },
    "fluxcd_source_controller": {
        "urls": [
            "https://raw.githubusercontent.com/fluxcd/source-controller/refs/heads/main/config/crd/bases/source.toolkit.fluxcd.io_gitrepositories.yaml",
            "https://raw.githubusercontent.com/fluxcd/source-controller/refs/heads/main/config/crd/bases/source.toolkit.fluxcd.io_helmcharts.yaml"
        ]
    },
    "fluxcd_helm_controller": {
        "urls": [
            "https://raw.githubusercontent.com/fluxcd/helm-controller/refs/heads/main/config/crd/bases/helm.toolkit.fluxcd.io_helmreleases.yaml"
        ]
    },
    "cert_manager": {
        "urls": [
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-certificaterequests.yaml",
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-certificates.yaml",
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-challenges.yaml",
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-clusterissuers.yaml",
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-issuers.yaml",
            "https://raw.githubusercontent.com/cert-manager/cert-manager/refs/heads/master/deploy/crds/crd-orders.yaml"
        ]
    },
    "crossplane": {
        "urls": [
            "https://raw.githubusercontent.com/crossplane/crossplane/refs/heads/main/cluster/crds/apiextensions.crossplane.io_compositeresourcedefinitions.yaml"
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
