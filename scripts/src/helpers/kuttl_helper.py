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
