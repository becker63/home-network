from configuration import KFile, ProjectFilters, PROJECT_ROOT
from lib.test_ext.test_factory import make_kcl_test
from helpers.kcl_helpers import Exec

@make_kcl_test(ProjectFilters.CONTROL)
def auto_generate_yaml_synth(pf: ProjectFilters, kf: KFile) -> None:
    synth_dir = PROJECT_ROOT / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"
    result = Exec(kf.path)
    output_path.write_text(result.yaml_result)
