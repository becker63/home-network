from configuration import KFile, ProjectFilters
from lib.test_factory import make_kcl_group_test
from pathlib import Path

def generateFrpStr(kf: KFile) -> str:
    return ""

def deployDockerFrps(config: str):
    pass

@make_kcl_group_test(["ClientConfig", "ServerConfig", "DaemonSet"], ProjectFilters.PROXY_E2E)
def e2e_frp_kuttl(clientconfig_kf: KFile, serverconfig_kf: KFile, daemonset_kf: KFile, tmp_path: Path) -> None:
    print("🛰️ ClientConfig:", clientconfig_kf)
    print("🚀 ServerConfig:", serverconfig_kf)
    print("🚀 DaemonSet:", daemonset_kf)
