import subprocess
from pathlib import Path

from configuration import KFile, ProjectFilters
from lib.test_ext.test_factory import make_kcl_group_test
from helpers.kcl_helpers import Exec

def run_frp_verify(name: str, kf: KFile, tmp_path: Path) -> None:
    config_path = tmp_path / f"{name}.json"
    config_path.write_text(Exec(kf.path).json_result)

    completed = subprocess.run(
        [name, "verify", f"--config={config_path}"],
        capture_output=True,
        check=False
    )

    assert completed.returncode == 0, (
        f"{name} verify failed\n"
        f"stdout: {completed.stdout.decode()}\n"
        f"stderr: {completed.stderr.decode()}"
    )

@make_kcl_group_test(["ClientConfig", "ServerConfig"], ProjectFilters.PROXY_TEST)
def check_frp_validate(clientconfig_kf: KFile, serverconfig_kf: KFile, tmp_path: Path) -> None:
    run_frp_verify("frpc", clientconfig_kf, tmp_path)
    run_frp_verify("frps", serverconfig_kf, tmp_path)
