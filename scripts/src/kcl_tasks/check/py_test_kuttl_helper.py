from helpers.kuttl_helper import run_kuttl_test
from pathlib import Path

def py_configmap_kuttl(tmp_path: Path):
    configmap_yaml = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-config
  namespace: default
data:
  hello: world
"""

    assert_yaml = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-config
  namespace: default
data:
  hello: world
"""

    run_kuttl_test(
        tmp_dir=tmp_path,
        test_name="configmap-check",
        resource_yaml=configmap_yaml,
        assert_yaml=assert_yaml,
        namespace="default"
    )
