import pytest
from pytest_print import Printer

from lib import KFile, PROJECT_ROOT
from helpers.kcl_helpers import Exec
from helpers.conftest_helpers import fileset

from project_config import ProjectFilters

@pytest.mark.automation
@fileset([ProjectFilters.BOOTSTRAP_SYNTH, ProjectFilters.BOOTSTRAP])
def test_generate_yaml_synth(
    filter_name: ProjectFilters,
    kf: KFile,
    printer: Printer,
):
    synth_dir = PROJECT_ROOT / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"

    result = Exec(kf.path)

    output_path.write_text(result.yaml_result)
