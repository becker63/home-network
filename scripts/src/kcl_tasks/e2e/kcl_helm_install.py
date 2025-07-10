from pathlib import Path
from configuration import KFile
from lib.test_ext.test_factory import make_kcl_named_test

@make_kcl_named_test(["crossplane_release.k"],  lambda kf: "helm_releases" in kf.path.parts )
def e2e_frp_kuttl(
    crossplane_release: KFile,
    tmp_path: Path
) -> None:
    print(crossplane_release.path)
