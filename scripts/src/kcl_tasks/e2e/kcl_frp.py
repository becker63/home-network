from pathlib import Path
from typing import Generator
from contextlib import contextmanager
import time
import textwrap

from configuration import KFile, ProjectFilters
from helpers.kcl_helpers import Exec, Override_file_tmp_multi
from helpers.helpers import get_free_port
from lib.test_factory import make_kcl_group_test
from helpers.kuttl_helper import run_kuttl_test

from docker import from_env as docker_from_env
from docker.models.containers import Container
from docker.models.images import Image


def build_frps_image_with_config(server_config_json: str, tmp_path: Path, tag: str = "test-frps:latest") -> Image:
    dockerfile = f"""
    FROM fatedier/frps:v0.62.1
    COPY frps.json /etc/frp/frps.json
    """
    build_dir = tmp_path / "frps_build"
    build_dir.mkdir(exist_ok=True)

    (build_dir / "Dockerfile").write_text(dockerfile)
    (build_dir / "frps.json").write_text(server_config_json)

    client = docker_from_env()
    image, _ = client.images.build(path=str(build_dir), tag=tag)
    return image


@contextmanager
def run_frps_container_with_yield(server_config_json: str, tmp_path: Path, bind_port: int = 7000) -> Generator[Container, None, None]:
    image_tag = "test-frps:latest"
    build_frps_image_with_config(server_config_json, tmp_path, tag=image_tag)

    client = docker_from_env()
    container = client.containers.run(
        image=image_tag,
        name="test-frps",
        command=["frps", "--config", "/etc/frp/frps.json"],
        ports={f"{bind_port}/tcp": bind_port},
        detach=True,
        remove=False,
    )

    try:
        timeout_secs = 5
        interval = 0.2
        elapsed = 0.0
        while elapsed < timeout_secs:
            container.reload()
            if container.status == "running":
                break
            time.sleep(interval)
            elapsed += interval
        else:
            raise RuntimeError(f"FRPS container did not start in time (status: {container.status})")

        yield container
    finally:
        try:
            container.stop(timeout=3)
        except Exception as e:
            print(f"[WARN] Failed to stop container: {e}")
        try:
            container.remove()
        except Exception as e:
            print(f"[WARN] Failed to remove container: {e}")


@make_kcl_group_test(["ClientConfig", "ServerConfig", "DaemonSet"], ProjectFilters.PROXY_E2E)
def e2e_frp_kuttl(clientconfig_kf: KFile, serverconfig_kf: KFile, daemonset_kf: KFile, tmp_path: Path) -> None:
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
        daemonset = Exec(daemonset_kf.path).yaml_result

        with run_frps_container_with_yield(serverconfig, tmp_path, bind_port=BINDPORT) as container:
            assert container.status == "running", "FRPS container failed to start"

            # Feed the daemonset and basic assert into KUTTL
            run_kuttl_test(
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
