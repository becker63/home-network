from crossplane.function.proto.v1 import run_function_pb2 as fnv1

def compose(req: fnv1.RunFunctionRequest, rsp: fnv1.RunFunctionResponse):
    # Look for the launch-instance resource in observed state
    instance = req.observed.resources.get("launch-instance")
    if instance and instance.resource:
        conditions = instance.resource.fields.get("status", {}).get("conditions", {}).get("fields", {})
        for cond in conditions.values():
            if (
                cond.get("fields", {}).get("type", {}).get("string_value") == "Ready" and
                cond.get("fields", {}).get("status", {}).get("string_value") == "True"
            ):
                rsp.desired.resources.pop("upload-image", None)
                break
