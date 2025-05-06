from invoke.tasks import task
from config import (
    NODES,
    CONFIG_DIR,
    TALOSCONFIG_PATH,
    KUBECONFIG_PATH,
)

@task
def bootstrap_cluster(c):
    """
    Bootstrap the Talos cluster from the first control plane node.
    """
    node_ip = get_bootstrap_node_ip()

    print(f"🚀 Bootstrapping from {node_ip}")
    c.run(
        f"talosctl bootstrap "
        f"--talosconfig {TALOSCONFIG_PATH} "
        f"--nodes {node_ip} "
        f"--endpoints {node_ip}",
        echo=True
    )

@task
def fetch_kubeconfig(c, force=False):
    """
    Fetch kubeconfig from Talos cluster.
    Skips if file already exists unless --force is passed.
    """
    node_ip = get_bootstrap_node_ip()

    if KUBECONFIG_PATH.exists() and not force:
        print(f"⚠️  kubeconfig already exists at {KUBECONFIG_PATH}. Use --force to overwrite.")
        return

    print(f"📦 Fetching kubeconfig from {node_ip}")
    c.run(
        f"talosctl kubeconfig "
        f"--talosconfig {TALOSCONFIG_PATH} "
        f"--nodes {node_ip} "
        f"--endpoints {node_ip} "
        f"{KUBECONFIG_PATH} --force",
        echo=True
    )

@task
def apply_config(c, node_ip):
    """
    Apply Talos machine config to the given node (insecure mode for first contact).
    """
    print(f"📦 Applying config to {node_ip}")
    hostname = resolve_hostname(node_ip)
    config_file = CONFIG_DIR / f"{hostname}.yaml"

    c.run(
        f"talosctl apply-config "
        f"--insecure "
        f"--nodes {node_ip} "
        f"--file {config_file}",
        echo=True
    )

# Helpers

def resolve_hostname(ip):
    for node in NODES:
        if node["ip"] == ip:
            return node["hostname"]
    return "unknown"

def get_bootstrap_node_ip():
    return NODES[0]["ip"]
