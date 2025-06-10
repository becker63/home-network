from pathlib import Path

from configuration import KFile, ProjectFilters
from lib.test_factory import make_kcl_test
from helpers.kcl_helpers import kcl_path_to_frp_relevant

@make_kcl_test(ProjectFilters.PROXY_E2E)
def e2e_frp_kuttl(pf: ProjectFilters, kf: KFile, tmp_path: Path) -> None:
    print(kcl_path_to_frp_relevant(kf, tmp_path), kf.path.name)
