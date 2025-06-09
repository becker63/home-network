from configuration import KFile, ProjectFilters
from kcl_tasks.parametizer import parametrize_kcl_files
from helpers.kcl_helpers import kcl_path_to_frp_relevant


@parametrize_kcl_files(ProjectFilters.PROXY_E2E)
def auto_generate_yaml_synth(pf: ProjectFilters, kf: KFile):
    print(kcl_path_to_frp_relevant(kf), kf.path.name)
