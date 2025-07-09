from typing import Any, Type, TypeVar, Dict, Tuple, List, cast
import yaml

from cloudcoil.models.kubernetes.apps.v1 import Deployment
from cloudcoil.models.kubernetes.core.v1 import Service

import cloudcoil.models.kubernetes.apps.v1 as apps_v1
import cloudcoil.models.kubernetes.core.v1 as core_v1

# Typing alias for any Cloudcoil model
CloudcoilModel = Any

MODEL_REGISTRY: Dict[Tuple[str, str], Type[CloudcoilModel]] = {
    ("apps/v1", "Deployment"): apps_v1.Deployment,
    ("v1", "Service"): core_v1.Service,
}


def parse_kcl_yaml(yaml_text: str) -> List[CloudcoilModel]:
    objs: List[CloudcoilModel] = []
    for raw_doc in yaml.safe_load_all(yaml_text):
        if not isinstance(raw_doc, dict):
            continue

        # Cast to concrete typed dict
        doc = cast(Dict[str, Any], raw_doc)

        api_version = doc.get("api_version") or doc.get("apiVersion")
        kind = doc.get("kind")

        if not isinstance(api_version, str) or not isinstance(kind, str):
            continue

        model_cls = MODEL_REGISTRY.get((api_version, kind))
        if model_cls is not None:
            obj = model_cls(**doc)  # type: ignore (if needed)
            objs.append(obj)

    return objs


T = TypeVar("T")

def find_first_of_type(resources: List[Any], typ: Type[T]) -> T:
    for res in resources:
        if isinstance(res, typ):
            return res
    raise ValueError(f"Type {typ} not found in resources")

# --- usage example below ---
yaml_input = """
api_version: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    match_labels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - container_port: 80
---
api_version: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    target_port: 80
"""

resources = parse_kcl_yaml(yaml_input)

# TODO: instead of just picking with isinstance the first type that matches from an array, create a match function that will allow me to fill in the second argument (the type) with some of the values I expect from the kcl, so that if Im for example given two deployments in the yaml I can select the one I need. For now this is fine.
deployment: Deployment = find_first_of_type(resources, Deployment)
service: Service = find_first_of_type(resources, Service)


out = yaml.dump(
    deployment.model_dump(exclude_none=True, exclude_unset=True)
)
print(out)
