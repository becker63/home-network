import pytest
from configuration import KFile, ProjectFilters
from kcl_tasks.parametizer import parametrize_kcl_files

# TODO: exp with kcl_libs json_ast api, im not using it here bc the ast is so complex
@parametrize_kcl_files(ProjectFilters.INFRA_KCL)
def check_has_main(pf: ProjectFilters, kf: KFile):
    source = kf.path.read_text(encoding="utf-8")

    # Check that 'main' is defined
    if "main =" not in source:
        pytest.fail(f"The KCL file {kf.path.absolute()} does not define a 'main' variable.")

    # Check that 'main' is used in manifests.yaml_stream(...)
    found = False
    for line in source.splitlines():
        if "manifests.yaml_stream" in line and "main" in line:
            found = True
            break

    assert found, f"'main' is not passed to manifests.yaml_stream(...) in {kf.path.absolute()}"
