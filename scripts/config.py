from pathlib import Path

# Core paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()

# Talos-specific paths
CONFIG_DIR = PROJECT_ROOT / "talosctl" / "bootstrap_config"
TALOSCONFIG_PATH = CONFIG_DIR / "talosconfig"
KUBECONFIG_PATH = PROJECT_ROOT / "kubeconfig.yaml"

# Cluster settings
CLUSTER_NAME = "home-lab"
K8S_ENDPOINT = "https://192.168.1.101:6443"

NODES = [
    {"hostname": "top_rice-crispy-treat", "ip": "192.168.1.101"},
    {"hostname": "cp2", "ip": "192.168.1.102"},
    {"hostname": "cp3", "ip": "192.168.1.103"},
]
