from invoke.tasks import task
import subprocess
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "nix_configs" / "cloud_frp" / "configuration.nix"
OUTPUT_IMAGE = PROJECT_ROOT / "nix_configs" / "terraform" / "nixos-frp.qcow2"

@task
def build_qcow_image(c):
    """
    Build a NixOS QCOW2 image from configuration.nix using nixos-generators.
    """
    print("🚀 Generating NixOS QCOW2 image...")

    cmd = (
        f"nix run github:nix-community/nixos-generators -- "
        f"-f qcow2 -c {CONFIG_PATH} -o {OUTPUT_IMAGE}"
    )

    c.run(cmd, echo=True)
    print(f"✅ QCOW2 image created at {OUTPUT_IMAGE}")
