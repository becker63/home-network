from configuration import KFile, ProjectFilters
from lib.test_factory import make_kcl_test

@make_kcl_test(ProjectFilters.BASE)
def check_has_export(pf: ProjectFilters, kf: KFile) -> None:
    with open(kf.path, "r") as file:
        content = file.read()
    assert "manifests.yaml_stream(" in content, (
        f'\n\n"manifests.yaml_stream" must export something for consistency: {kf.path}\n\n'
    )
