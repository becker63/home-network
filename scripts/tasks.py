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
def bootstrap(c, node_ip="192.168.1.101"):
    """
    Bootstrap the Talos cluster on the first control plane node
    """
    print(f"🚀 Bootstrapping cluster on {node_ip}...")
    result = c.run(
        f"talosctl --talosconfig {CONFIG_DIR}/talosconfig bootstrap --nodes {node_ip}",
        echo=True,
        warn=True
    )
    if result.failed:
        print("❌ Bootstrap failed.")
    else:
        print("✅ Bootstrap successful.")
