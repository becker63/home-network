from __future__ import annotations

import subprocess
import sys
from typing import List
from configuration.configuration import CRD_SPECS


def run(cmd: List[str], check: bool = True) -> None:
    print(f"🏃 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=check, stdout=sys.stdout, stderr=sys.stderr)


def helm_release_exists(name: str, namespace: str) -> bool:
    result = subprocess.run(
        ["helm", "list", "--namespace", namespace, "--filter", f"^{name}$", "--short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip() == name


def install_crossplane() -> None:
    print("📦 Ensuring Crossplane is installed via Helm...")

    run(["helm", "repo", "add", "crossplane-stable", "https://charts.crossplane.io/stable"])
    run(["helm", "repo", "update"])

    release_name = "crossplane"
    namespace = "crossplane-system"

    if helm_release_exists(release_name, namespace):
        print(f"🔁 Helm release '{release_name}' exists. Upgrading...")
        run([
            "helm", "upgrade", release_name, "crossplane-stable/crossplane",
            "--namespace", namespace
        ])
    else:
        print(f"🚀 Installing Helm release '{release_name}'...")
        run([
            "helm", "install", release_name, "crossplane-stable/crossplane",
            "--namespace", namespace, "--create-namespace"
        ])


def apply_crd_from_url(url: str) -> None:
    print(f"🔧 Applying CRD from {url}")
    try:
        subprocess.run(
            ["kubectl", "apply", "-f", url],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to apply CRD: {url}")
        raise e


def apply_crossplane_crds() -> None:
    print("📄 Applying additional Crossplane-related CRDs...")
    for _name, spec in CRD_SPECS.items():
        for url in spec.get("urls", []):
            apply_crd_from_url(url)
    print("✅ All Crossplane CRDs applied.")


def main() -> None:
    install_crossplane()
    apply_crossplane_crds()


if __name__ == "__main__":
    main()
