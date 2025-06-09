from configuration import KFile, ProjectFilters
from helpers.kcl_helpers import Exec
from kcl_tasks.parametizer import parametrize_kcl_files
from helpers.kcl_helpers import kcl_path_to_frp_relevant, FRPTYPE
import subprocess
from pathlib import Path
import pytest

FRP_COMMANDS = {
    FRPTYPE.FRPC: "frpc",
    FRPTYPE.FRPS: "frps",
}

@parametrize_kcl_files(ProjectFilters.PROXY_TEST)
def check_frp_validate(pf: ProjectFilters, kf: KFile, tmp_path: Path) -> None:
    frp_type = kcl_path_to_frp_relevant(kf)
    command = FRP_COMMANDS.get(frp_type)

    if not command:
        pytest.skip(f"No FRP binary matched for {kf.path.name} (type={frp_type})")

    result = Exec(kf.path).json_result
    config_path = tmp_path / "test.json"
    config_path.write_text(result)

    completed = subprocess.run(
        [command, "verify", f"--config={config_path}"],
        capture_output=True,
        check=False
    )

    assert completed.returncode == 0, (
        f"{command} verify failed\n"
        f"stdout: {completed.stdout.decode()}\n"
        f"stderr: {completed.stderr.decode()}"
    )
