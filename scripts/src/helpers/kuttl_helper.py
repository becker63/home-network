import subprocess
from pathlib import Path
from subprocess import CompletedProcess



def run_kuttl_test(
    tmp_dir: Path,
    test_name: str,
    resource_yaml: str,
    assert_yaml: str,
    timeout: int = 20,
    namespace: str = "default",
    start_kind_cluster: bool = False,
) -> CompletedProcess[str]:

    test_dir = tmp_dir / test_name
    test_dir.mkdir(parents=True, exist_ok=True)

    (test_dir / "test.yaml").write_text(resource_yaml)
    (test_dir / "assert.yaml").write_text(assert_yaml)

    cmd = [
        "kubectl", "kuttl", "test", str(test_dir),
        "--timeout", str(timeout),
        "--namespace", namespace,
    ]

    # Return process object to inspect exit code or output
    return subprocess.run(cmd, capture_output=True, text=True)
