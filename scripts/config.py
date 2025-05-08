from pathlib import Path

def find_project_root(start: Path, marker_file: str = "Justfile") -> Path:
    current = start
    while current != current.parent:
        if (current / marker_file).exists():
            return current
        current = current.parent
    raise RuntimeError("Project root not found.")

# Core paths
PROJECT_ROOT = find_project_root(Path(__file__).resolve())
PHASES_DIR = PROJECT_ROOT / "phases"

# Talos-specific paths
CONFIG_DIR = PROJECT_ROOT / "talosctl" / "bootstrap_config"
TALOSCONFIG_PATH = CONFIG_DIR / "talosconfig"
KUBECONFIG_PATH = PROJECT_ROOT / "kubeconfigs"

# Cluster settings
CLUSTER_NAME = "home-lab"
K8S_ENDPOINT = "https://192.168.1.101:6443"

NODES = [
    {"hostname": "top_rice-crispy-treat", "ip": "192.168.1.101"},
    {"hostname": "cp2", "ip": "192.168.1.102"},
    {"hostname": "cp3", "ip": "192.168.1.103"},
]
