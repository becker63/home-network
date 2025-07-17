#from pathlib import Path
from configuration import KFile
from lib.test_ext.test_factory import make_kcl_named_test
import json
from helpers.kcl_helpers import Exec
from ccgen.fluxcd_helm_controller.io.fluxcd.toolkit.helm.v2 import HelmRelease
from cloudcoil.resources import Unstructured
from cloudcoil.models.kubernetes.core.v1 import Namespace
from cloudcoil.errors import ResourceNotFound
import subprocess
import pytest
import yaml


@pytest.mark.configure_test_cluster(
    cluster_name="shared-cluster",
    remove=False  # Keep cluster after tests
)
@make_kcl_named_test(["crossplane_release.k"],  lambda kf: "helm_releases" in kf.path.parts )
def e2e_frp_kuttl(
    crossplane_release: KFile
) -> None:
    subprocess.run(["flux", "run"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    kcl = Exec(crossplane_release.path)

    dict = json.loads(kcl.json_result)
    release = HelmRelease.model_validate(dict)

    assert release.metadata != None
    metadata = release.metadata

    if metadata.namespace is None:
        raise ValueError("HelmRelease.metadata.namespace and name is required")
    if metadata.name is None:
        raise ValueError("HelmRelease.metadata.name is required")


    try:
        Namespace.get(name=metadata.namespace)
        print(f"Namespace '{metadata.namespace}' already exists.")
    except ResourceNotFound:
        ns = Namespace.builder() \
            .metadata(lambda m: m.name(metadata.namespace)) \
            .build() \
            .create()

        for event, _ in ns.watch():
            if event == "ADDED":
                print("namespace added")
                break


    try:
        HelmRelease.get(name=metadata.name, namespace=metadata.namespace)
        print(f"HelmRelease '{metadata.name}' already exists.")
    except ResourceNotFound:
        release = release.create()

        for event, _ in release.watch(namespace=metadata.namespace):
            if event == "BOOKMARK":
                    print("Skipping BOOKMARK event")
                    continue

            if event == "ADDED":
                print(f"HelmRelease '{metadata.name}' successfully created.")
                break
