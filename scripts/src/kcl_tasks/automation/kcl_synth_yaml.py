from lib.config_interface import PROJECT_ROOT
from lib.runtime_config import KFile, ProjectFilters
from helpers.kcl_helpers import Exec
from kcl_tasks.parametizer import parametrize_kcl_files


@parametrize_kcl_files(ProjectFilters.BOOTSTRAP)
def test_generate_yaml_synth(pf: ProjectFilters, kf: KFile):
    synth_dir = PROJECT_ROOT / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"
    result = Exec(kf.path)
    output_path.write_text(result.yaml_result)
