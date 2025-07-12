from pathlib import Path
from configuration import KFile
from lib.test_ext.test_factory import make_kcl_named_test
import json
from helpers.kcl_helpers import Exec
from ccgen.fluxcd_helm_controller.io.fluxcd.toolkit.helm.v2 import HelmRelease
from typing import Generator, Type, TypeVar, Any
from pydantic import BaseModel, ValidationError
from cloudcoil.apimachinery import ObjectMeta
from typing import cast

T = TypeVar("T", bound=BaseModel)

def safe_validate(model: Type[T], obj: dict[Any,Any]) -> Generator[T, None, None]:
    try:
        yield model.model_validate(obj)
    except ValidationError as e:
        print(f"⚠️ Invalid {model.__name__}: {e}")

@make_kcl_named_test(["crossplane_release.k"],  lambda kf: "helm_releases" in kf.path.parts )
def e2e_frp_kuttl(
    crossplane_release: KFile,
    tmp_path: Path
) -> None:
    kcl = Exec(crossplane_release.path).json_result
    dict = json.loads(kcl)

    release = HelmRelease.model_validate(dict)

    # some bs we gotta do bc they did not codegen correctly
    metadata = cast(ObjectMeta, release.metadata)
    print("cast:", metadata)
    print("def:", release.metadata)

    newdict = release.model_dump(by_alias=True, exclude_unset=False, exclude_none=True)
    print("new: \n", newdict)
    print("old: \n", dict)

    print("name: ", metadata.name)

    #for _, resource in release.watch(field_selector=f"metadata.name={metadata.name}"):
    #    for typed_resource in safe_validate(HelmRelease, resource.model_dump(by_alias=True)):
    #        # Now typed_resource is guaranteed and Pyright is happy
    #        if typed_resource.status and typed_resource.status.conditions:
    #            for condition in typed_resource.status.conditions:
    #                print(condition)
