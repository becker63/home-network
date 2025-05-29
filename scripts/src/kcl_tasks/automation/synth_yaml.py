import pytest
from fixtures import find_kcl_files, DirEnum
from helpers import find_project_root
import kcl_lib.api as api

# Only include KCL files not in FRP_SCHEMA
kcl_files = find_kcl_files(
    root=find_project_root() / "kcl",
    filter_fn=lambda kf: kf.dirname == DirEnum.BOOTSTRAP
)

# Fail clearly if no input files found
if not kcl_files:
    raise RuntimeError("No KCL files found under kcl/infra/. Cannot synthesize YAML.")

@pytest.mark.automation
@pytest.mark.parametrize("kf", kcl_files)
def test_generate_yaml_synth(kf):
    print(f"Running test_generate_yaml_synth for {kf.path}")
    synth_dir = find_project_root() / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"

    # Find the kcl.mod root
    mod_root = find_project_root() / "kcl"

    # Load external packages via kcl.mod
    kcl_api = api.API()
    deps_args = api.UpdateDependencies_Args(manifest_path=str(mod_root))
    deps_result = kcl_api.update_dependencies(deps_args)

    # Run the actual KCL file with external packages
    exec_args = api.ExecProgram_Args(
        k_filename_list=[str(kf.path)],
        external_pkgs=deps_result.external_pkgs
    )
    result = kcl_api.exec_program(exec_args)

    output_path.write_text(result.yaml_result)
