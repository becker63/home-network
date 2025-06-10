import pytest

from configuration import KFile, ProjectFilters
from kcl_tasks.parametizer import filter_kcl_files

@pytest.mark.parametrize(
    "pf, kf",
    filter_kcl_files(ProjectFilters.BASE)
)
def check_has_export(pf: ProjectFilters, kf: KFile) -> None:
    with open(kf.path, "r") as file:
        content = file.read()
    assert "manifests.yaml_stream(" in content, (
        f'\n\n"manifests.yaml_stream" must export something for consistency: {kf.path}\n\n'
    )
