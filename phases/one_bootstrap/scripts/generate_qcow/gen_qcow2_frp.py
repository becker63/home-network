from invoke.tasks import task
from pathlib import Path

# Paths
PHASE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PHASE_ROOT / "nix_configs" / "cloud_frp" / "configuration.nix"
OUTPUT_IMAGE = PHASE_ROOT / "terraform" / "nixos-frp.qcow2"

@task
def build_qcow_image(c):
    """
    Build a NixOS QCOW2 image from configuration.nix using nixos-generators.
    """
    print("🚀 Generating NixOS QCOW2 image...")

    cmd = (
        f"NIXPKGS_ALLOW_UNSUPPORTED_SYSTEM=1 "
        f"nix build --impure --extra-platforms x86_64-linux "
        f".#qcowImage"
    )

    c.run(cmd, echo=True)
    print(f"✅ QCOW2 image created at {OUTPUT_IMAGE}")
