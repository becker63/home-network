from helpers.kuttl_helper import run_kuttl_test
from pathlib import Path

def py_configmap_kuttl(tmp_path: Path):
    resource = """
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: test-map
    data:
      foo: bar
    """
    assert_yaml = """
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: test-map
    data:
      foo: bar
    """

    run_kuttl_test(tmp_dir=tmp_path, test_name="quiet-pass", resource_yaml=resource, assert_yaml=assert_yaml)
