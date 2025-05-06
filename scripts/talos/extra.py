from invoke.tasks import task
from config import (
    NODES,
    TALOSCONFIG_PATH,
)

@task
def health_check(c):
    """
    Check Talos and Kubernetes health across all nodes using talosctl health.
    """
    ip = NODES[0]["ip"]
    print("🔍 Checking health of cluster.")
    c.run(
        f"talosctl health "
        f"--talosconfig {TALOSCONFIG_PATH} "
        f"--nodes {ip} "
        f"--endpoints {ip}",
        warn=True,
        echo=True
        )
