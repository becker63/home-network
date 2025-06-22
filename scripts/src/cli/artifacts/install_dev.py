from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List
from configuration.configuration import CRD_SPECS


def run(cmd: List[str], check: bool = True, cwd: str | None = None) -> subprocess.CompletedProcess:
    print(f"🏃 Running: {' '.join(cmd)} (in {cwd or 'current dir'})")
    return subprocess.run(cmd, check=check, cwd=cwd, stdout=sys.stdout, stderr=sys.stderr)


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
        run(["kubectl", "apply", "-f", url])
    except subprocess.CalledProcessError:
        print(f"❌ Failed to apply CRD: {url}")
        raise


def apply_crossplane_crds() -> None:
    print("📄 Applying additional Crossplane-related CRDs...")
    for _name, spec in CRD_SPECS.items():
        for url in spec.get("urls", []):
            apply_crd_from_url(url)
    print("✅ All Crossplane CRDs applied.")


def install_kcl_operator() -> None:
    print("⚙️ Installing KCL Operator using a temporary directory...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        repo_url = "https://github.com/kcl-lang/kcl-operator.git"
        repo_path = tmp_path / "kcl-operator"

        # Clone the repo
        run(["git", "clone", "--depth", "1", repo_url, str(repo_path)])

        # Run `make deploy` in the repo
        print("🔧 Running make deploy...")
        run(["make", "deploy"], cwd=str(repo_path))

    print("✅ KCL Operator installed and temp dir cleaned up.")


def main() -> None:
    install_crossplane()
    apply_crossplane_crds()
    install_kcl_operator()


if __name__ == "__main__":
    main()
