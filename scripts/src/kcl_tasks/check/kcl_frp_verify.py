import subprocess
from pathlib import Path

import pytest

from configuration import KFile, ProjectFilters
from lib.filter import filter_kcl_files
from helpers.kcl_helpers import Exec, kcl_path_to_frp_relevant, FRPTYPE

FRP_COMMANDS = {
    FRPTYPE.FRPC: "frpc",
    FRPTYPE.FRPS: "frps",
}

@pytest.mark.parametrize(
    "pf, kf",
    filter_kcl_files(ProjectFilters.PROXY_TEST)
)
def check_frp_validate(pf: ProjectFilters, kf: KFile, tmp_path: Path) -> None:
    frp_type = kcl_path_to_frp_relevant(kf, tmp_path)
    command = FRP_COMMANDS.get(frp_type)

    if not command:
        pytest.skip(f"No FRP binary matched for {kf.path.name} (type={frp_type})")

    config_path = tmp_path / "test.json"
    config_path.write_text(Exec(kf.path).json_result)

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
