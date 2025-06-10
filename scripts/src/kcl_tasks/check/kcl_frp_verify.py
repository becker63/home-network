import subprocess
from pathlib import Path

from configuration import KFile, ProjectFilters
from lib.test_factory import make_kcl_group_test
from helpers.kcl_helpers import Exec


@make_kcl_group_test(["ClientConfig", "ServerConfig"], ProjectFilters.PROXY_TEST)
def check_frp_validate(clientconfig_kf: KFile, serverconfig_kf: KFile, tmp_path: Path) -> None:
    def run_frp_verify(name: str, kf: KFile) -> None:
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

    run_frp_verify("frpc", clientconfig_kf)
    run_frp_verify("frps", serverconfig_kf)
