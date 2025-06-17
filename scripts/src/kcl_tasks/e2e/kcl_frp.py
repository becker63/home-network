from pathlib import Path
from typing import Generator, Optional
from contextlib import contextmanager
import textwrap
import json

from configuration import KFile, ProjectFilters
from helpers.kcl_helpers import Exec, Override_file_tmp_multi
from helpers.helpers import get_free_port
from lib.test_factory import make_kcl_group_test
from helpers.kuttl_helper import run_kuttl_test
import helpers.docker_helper as docker_helper

from docker import from_env as docker_from_env
from docker.models.containers import Container
from docker.models.images import Image


def build_frps_image_with_config(
    server_config_json: str,
    tmp_path: Path,
    version: str,
    tag: Optional[str] = None
) -> Image:
    base_image_tag = f"fatedier/frps:{version}"
    image_tag = tag or f"test-frps:{version}"

    dockerfile: str = f"""
    FROM {base_image_tag}
    COPY frps.json /etc/frp/frps.json
    """

    build_dir: Path = tmp_path / "frps_build"
    build_dir.mkdir(exist_ok=True)

    (build_dir / "Dockerfile").write_text(dockerfile)
    (build_dir / "frps.json").write_text(server_config_json)

    client = docker_from_env()
    image, _ = client.images.build(path=str(build_dir), tag=image_tag)
    return image


@contextmanager
def Run_frps_container(
    server_config_json: str,
    tmp_path: Path,
    version: str,
    bind_port: int = 7000
) -> Generator[Container, None, None]:
    image_tag = f"test-frps:{version}"
    build_frps_image_with_config(server_config_json, tmp_path, version=version, tag=image_tag)

    client = docker_from_env()
    container: Container = client.containers.run(
        image=image_tag,
        name="test-frps",
        command=["frps", "--config", "/etc/frp/frps.json"],
        ports={f"{bind_port}/tcp": bind_port},
        detach=True,
        remove=False,
    )

    try:
        docker_helper.wait_for_container_running(container)
        yield container
    finally:
        docker_helper.stop_and_remove_container(container)


@make_kcl_group_test(["clientconfig = Client.ClientConfig", "serverconfig = Server.ServerConfig", "frpc-daemonset"], ProjectFilters.PROXY_E2E)
def e2e_frp_kuttl(
    clientconfig_kf: KFile,
    serverconfig_kf: KFile,
    frpc_daemonset_kf: KFile,
    tmp_path: Path
) -> None:
    SERVERADDR = "localhost"
    BINDPORT = get_free_port()

    overrides = {
        clientconfig_kf.path: [
            f'clientconfig.serverAddr="{SERVERADDR}"',
            f'clientconfig.serverPort={BINDPORT}',
        ],
        serverconfig_kf.path: [
            f'serverconfig.bindAddr="{SERVERADDR}"',
            f'serverconfig.bindPort={BINDPORT}',
        ],
    }

    with Override_file_tmp_multi(overrides):
        serverconfig = Exec(serverconfig_kf.path).json_result
        daemonset = Exec(frpc_daemonset_kf.path).yaml_result

        version_raw = json.loads(serverconfig).get("version")
        if not isinstance(version_raw, str):
            raise ValueError("Expected 'version' field to be a string in server config.")
        version: str = version_raw

        with Run_frps_container(server_config_json=serverconfig, tmp_path=tmp_path, version=version, bind_port=BINDPORT) as container:
            assert container.status == "running", "FRPS container failed to start"

            result = run_kuttl_test(
                tmp_dir=tmp_path,
                test_name="frpc-daemonset-check",
                resource_yaml=daemonset,
                assert_yaml=textwrap.dedent("""
                    apiVersion: apps/v1
                    kind: DaemonSet
                    metadata:
                      name: frpc-daemonset
                      namespace: kube-system
                    status:
                      numberReady: 1
                """),
                timeout=30,
                namespace="kube-system",
            )

            assert result.returncode == 0, (
                f"KUTTL test failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
