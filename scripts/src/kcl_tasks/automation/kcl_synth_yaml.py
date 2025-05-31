import pytest
from pytest_print import Printer

from lib import KFile
from lib.helpers import find_project_root
from lib.kcl_helpers import Exec
from lib.conftest_helpers import parametrize_files_for_group

from kcl_tasks.filters import ProjectFilters

@pytest.mark.automation
@parametrize_files_for_group([ ProjectFilters.BOOTSTRAP_SYNTH, ProjectFilters.BOOTSTRAP])
def test_generate_yaml_synth(
    filter_name: ProjectFilters,
    kf: KFile,
    printer: Printer
):
    root = find_project_root()
    synth_dir = root / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"

    result = Exec(kf.path)

    output_path.write_text(result.yaml_result)
