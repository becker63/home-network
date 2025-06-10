import pytest

from configuration import PROJECT_ROOT, KFile, ProjectFilters
from lib.filter import filter_kcl_files
from helpers.kcl_helpers import Exec

@pytest.mark.parametrize(
    "pf, kf",
    filter_kcl_files(ProjectFilters.BASE)
)
def auto_generate_yaml_synth(pf: ProjectFilters, kf: KFile) -> None:
    synth_dir = PROJECT_ROOT / "synth_yaml"
    synth_dir.mkdir(parents=True, exist_ok=True)

    output_path = synth_dir / f"{kf.path.stem}.yaml"
    result = Exec(kf.path)
    output_path.write_text(result.yaml_result)
