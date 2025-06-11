from configuration import KFile, ProjectFilters
from helpers.kcl_helpers import Exec, ListVariables, Override_file_tmp_multi
from lib.test_factory import make_kcl_group_test
from typing import List, Dict, Any, TypedDict


class ProxyEntry(TypedDict):
    name: str
    remotePort: int

# Protobuf is so confusing
def extract_services_for_sock_test(kcl_dict: Dict[str, Any]) -> List[ProxyEntry]:
    proxies: List[ProxyEntry] = []
    list_items = kcl_dict["variables"]["services"]["variables"][0]["listItems"]
    for proxy in list_items:
        fields = {e["key"]: e["value"]["value"].strip('"') for e in proxy["dictEntries"]}
        proxies.append({
            "name": fields["name"],
            "remotePort": int(fields["remotePort"]),
        })
    return proxies

@make_kcl_group_test(["ClientConfig", "ServerConfig", "DaemonSet"], ProjectFilters.PROXY_E2E)
def e2e_frp_kuttl(clientconfig_kf: KFile, serverconfig_kf: KFile, daemonset_kf: KFile) -> None:

    SERVERADDR = "localhost"

    # TODO: bind port
    overrides = {
        clientconfig_kf.path: [f'clientconfig.serverAddr="{SERVERADDR}"'],
        serverconfig_kf.path: [f'serverconfig.bindAddr="{SERVERADDR}"'],
    }

    with Override_file_tmp_multi(overrides):
        clientconfig = Exec(clientconfig_kf.path).json_result
        serverconfig = Exec(serverconfig_kf.path).json_result

        daemonset = Exec(daemonset_kf.path).yaml_result

        services = extract_services_for_sock_test(ListVariables(clientconfig_kf.path))

    # For now, just print these
    print(clientconfig)
    print(serverconfig)
    print(daemonset)
    print(services)
