from configuration import KFile, ProjectFilters
from helpers.kcl_helpers import Exec
from kcl_tasks.parametizer import parametrize_kcl_files
import subprocess
from pathlib import Path
import pytest


# Mapping from config file name to frp command
COMMAND_MAP = {
    "FRPC_Config.k": "frpc",
    "FRPS_Config.k": "frps",
}


@parametrize_kcl_files(ProjectFilters.PROXY_TEST)
def check_frp_validate(pf: ProjectFilters, kf: KFile, tmp_path: Path) -> None:
    command = COMMAND_MAP.get(kf.path.name)
    if not command:
        pytest.skip(f"No frp command mapped for {kf.path.name}")

    result = Exec(kf.path).json_result
    config_path = tmp_path / "test.json"

    config_path.write_text(result)

    completed = subprocess.run(
        [command, "verify", f"--config={config_path}"],
        capture_output=True,
        check=False
    )

    assert completed.returncode == 0, f"{command} verify failed"
