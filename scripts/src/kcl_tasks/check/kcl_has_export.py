from configuration import KFile, ProjectFilters
from lib.test_factory import make_kcl_test

@make_kcl_test(ProjectFilters.BASE)
def check_has_export(pf: ProjectFilters, kf: KFile) -> None:
    content = kf.path.read_text()
    assert "manifests.yaml_stream(" in content, (
        f'\n\nmust include "manifests.yaml_stream" and must export something for consistency: {kf.path}\n\n'
    )
