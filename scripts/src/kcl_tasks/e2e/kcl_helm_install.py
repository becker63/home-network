import json
import subprocess
from configuration import KFile
from lib.test_ext.test_factory import make_kcl_named_test
from helpers.kcl_helpers import Exec
from ccgen.fluxcd_helm_controller.io.fluxcd.toolkit.helm.v2 import HelmRelease
from cloudcoil.models.kubernetes.core.v1 import Namespace
from cloudcoil.errors import ResourceNotFound

@make_kcl_named_test(["crossplane_release.k"], lambda kf: "helm_releases" in kf.path.parts)
def e2e_frp_kuttl(crossplane_release: KFile) -> None:
    subprocess.run(["flux", "run"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    release = HelmRelease.model_validate(json.loads(Exec(crossplane_release.path).json_result))
    metadata = release.metadata

    if not metadata or not metadata.namespace or not metadata.name:
        raise ValueError("HelmRelease.metadata.namespace and name are required")

    try:
        Namespace.get(name=metadata.namespace)
        print(f"Namespace '{metadata.namespace}' already exists.")
    except ResourceNotFound:
        ns = Namespace.builder().metadata(lambda m: m.name(metadata.namespace)).build().create()
        for event, _ in ns.watch():
            if event == "ADDED":
                print("Namespace added")
                break

    try:
        HelmRelease.get(name=metadata.name, namespace=metadata.namespace)
        print(f"HelmRelease '{metadata.name}' already exists.")
    except ResourceNotFound:
        for event, _ in release.create().watch(namespace=metadata.namespace):
            if event == "BOOKMARK":
                continue
            if event == "ADDED":
                print(f"HelmRelease '{metadata.name}' successfully created.")
                break
