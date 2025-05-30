import pytest
from kcl_lib import api
from pytest_print import Printer

from lib.common import KFile
from lib.helpers import find_project_root
from lib.conftest_helpers import parametrize_files_for_group
from kcl_tasks.filters import ProjectFilters

@pytest.mark.automation
@parametrize_files_for_group([ProjectFilters.BOOTSTRAP, ProjectFilters.BOOTSTRAP_SYNTH])
def test_generate_yaml_synth(
    filter_name: ProjectFilters,
    kf: KFile,
    printer: Printer
):
    root = find_project_root()
    synth_dir = root / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"

    mod_root = find_project_root() / "kcl"
    kcl_api = api.API()

    deps_args = api.UpdateDependencies_Args(manifest_path=str(mod_root))
    deps_result = kcl_api.update_dependencies(deps_args)

    exec_args = api.ExecProgram_Args(
        k_filename_list=[str(kf.path)],
            external_pkgs=deps_result.external_pkgs
    )
    result = kcl_api.exec_program(exec_args)

    output_path.write_text(result.yaml_result)
