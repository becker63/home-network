import pytest
from typing import Dict, List
from kcl_lib import api

from lib.common import KFile, ProjectFilters
from lib.helpers import find_project_root
from lib.conftest_helpers import parametrize_group



@pytest.mark.automation
@parametrize_group(ProjectFilters.BOOTSTRAP)
def test_generate_yaml_synth(
    filter_name: ProjectFilters,
    kcl_files_by_filter: Dict[ProjectFilters, List[KFile]]
):
    files = kcl_files_by_filter[filter_name]
    assert files, f"No files found for filter '{filter_name}'"

    for kf in files:
        print(f"Running test_generate_yaml_synth for {kf.path}")
        synth_dir = find_project_root() / "synth_yaml"
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
