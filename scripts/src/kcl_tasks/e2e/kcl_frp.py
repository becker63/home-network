import pytest
from pathlib import Path

from configuration import KFile, ProjectFilters
from lib.filter import filter_kcl_files
from helpers.kcl_helpers import kcl_path_to_frp_relevant

@pytest.mark.parametrize(
    "pf, kf",
    filter_kcl_files(ProjectFilters.PROXY_E2E)
)
def e2e_frp_kuttl(pf: ProjectFilters, kf: KFile, tmp_path: Path) -> None:
    print(kcl_path_to_frp_relevant(kf, tmp_path), kf.path.name)
