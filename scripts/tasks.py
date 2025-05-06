from invoke.tasks import task
from pathlib import Path
import yaml

# Cluster settings
CLUSTER_NAME = "home-lab"
K8S_ENDPOINT = "https://192.168.1.101:6443"

NODES = [
    {"hostname": "top_rice-crispy-treat", "ip": "192.168.1.101"},
    {"hostname": "cp2", "ip": "192.168.1.102"},
    {"hostname": "cp3", "ip": "192.168.1.103"},
]

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = (PROJECT_ROOT / "talosctl" / "bootstrap_config").resolve()
KUBECONFIG_PATH = (PROJECT_ROOT / "kubeconfig.yaml").resolve()

@task
def generate(c):
    """
    Generate cluster and machine configs
    """
    print(f"📦 Generating Talos config in {CONFIG_DIR}")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    result = c.run(
        f"talosctl gen config {CLUSTER_NAME} {K8S_ENDPOINT} --output-dir {CONFIG_DIR} --force",
        echo=True,
        warn=True
    )

    if result.failed:
        print("❌ talosctl gen config failed.")
        return

    template_path = CONFIG_DIR / "controlplane.yaml"
    if not template_path.exists():
        print("❌ controlplane.yaml not found.")
        return

    with template_path.open() as f:
        controlplane_template = yaml.safe_load(f)

    for node in NODES:
        config = controlplane_template.copy()
        config["machine"]["network"] = {
            "interfaces": [{
                "interface": "eth0",
                "addresses": [f"{node['ip']}/24"],
                "dhcp": False,
            }],
            "hostname": node["hostname"]
        }

        output_path = CONFIG_DIR / f"{node['hostname']}.yaml"
        with output_path.open("w") as f:
            yaml.dump(config, f)

        print(f"✅ Wrote config: {output_path}")


@task
def apply_config(c, node_ip):
    """
    Apply Talos machine config to the given node.
    """
    print(f"📦 Applying config to {node_ip}")
    c.run(
        f"talosctl apply-config "
        f"--talosconfig {CONFIG_DIR/'talosconfig'} "
        f"--nodes {node_ip} "
        f"--endpoints {node_ip} "
        f"--file {CONFIG_DIR/f'{resolve_hostname(node_ip)}.yaml'}",
        echo=True
    )


@task
def bootstrap_cluster(c):
    """
    Bootstrap the Talos cluster from the first control plane node.
    Skips if kubeconfig already exists.
    """
    node_ip = get_bootstrap_node_ip()

    if KUBECONFIG_PATH.exists():
        print("⚠️  Cluster already bootstrapped. Skipping bootstrap.")
        return

    print(f"🚀 Bootstrapping from {node_ip}")
    c.run(
        f"talosctl bootstrap "
        f"--talosconfig {CONFIG_DIR/'talosconfig'} "
        f"--nodes {node_ip} "
        f"--endpoints {node_ip}",
        echo=True
    )

    print("📦 Fetching kubeconfig")
    c.run(
        f"talosctl kubeconfig "
        f"--talosconfig {CONFIG_DIR/'talosconfig'} "
        f"--nodes {node_ip} "
        f"--endpoints {node_ip} "
        f"{KUBECONFIG_PATH} --force",
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
