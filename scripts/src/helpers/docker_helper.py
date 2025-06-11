import time
from docker.models.containers import Container


def wait_for_container_running(container: Container, timeout_secs: float = 5.0, interval: float = 0.2) -> None:
    elapsed = 0.0
    while elapsed < timeout_secs:
        container.reload()
        if container.status == "running":
            return
        time.sleep(interval)
        elapsed += interval
    raise RuntimeError(f"Container did not start in time (status: {container.status})")


def stop_and_remove_container(container: Container, timeout: int = 3) -> None:
    try:
        container.stop(timeout=timeout)
    except Exception as e:
        print(f"[WARN] Failed to stop container: {e}")
    try:
        container.remove()
    except Exception as e:
        print(f"[WARN] Failed to remove container: {e}")
