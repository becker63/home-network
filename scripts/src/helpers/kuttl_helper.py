import subprocess
from pathlib import Path


def run_kuttl_test(
    tmp_dir: Path,
    test_name: str,
    resource_yaml: str,
    assert_yaml: str,
    timeout: int = 20,
    namespace: str = "default",
    start_kind_cluster: bool = False,
) -> None:
    """
    Writes KUTTL resource and assert YAMLs into a temporary directory and runs `kuttl test`.

    :param tmp_dir: The pytest-provided temporary directory (e.g., tmp_path)
    :param test_name: A name for this test, used as the directory name within tmp_dir
    :param resource_yaml: The resource YAML content (e.g., a DaemonSet)
    :param assert_yaml: The assert YAML content (e.g., an assert on DaemonSet ready)
    :param timeout: KUTTL test timeout in seconds
    :param namespace: Kubernetes namespace for the test
    :param start_kind_cluster: Whether to let KUTTL start a kind cluster
    """

    test_dir = tmp_dir / test_name
    test_dir.mkdir(parents=True, exist_ok=True)

    # Write test.yaml (resources to apply)
    test_yaml_path = test_dir / "test.yaml"
    test_yaml_path.write_text(resource_yaml)

    # Write assert.yaml (expected state)
    assert_yaml_path = test_dir / "assert.yaml"
    assert_yaml_path.write_text(assert_yaml)

    # Run kuttl test
    cmd = [
        "kubectl", "kuttl", "test", str(test_dir),
        "--timeout", str(timeout),
        "--namespace", namespace,
    ]

    subprocess.run(cmd, check=True)
