#!/usr/bin/env python3

import subprocess
import urllib.request
import tempfile
from pathlib import Path
from configuration import CRD_SPECS, SCHEMA_ROOT


def download(url: str, dest: Path) -> None:
    print(f"📥 Downloading {url}")
    with urllib.request.urlopen(url) as response:
        dest.write_bytes(response.read())


def fetch_crds() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        for name, spec in CRD_SPECS.items():
            print(f"\n📦 Fetching {name} CRDs...")
            schema_dir = SCHEMA_ROOT / name
            schema_dir.mkdir(parents=True, exist_ok=True)

            crd_dir = tmp_path / name
            crd_dir.mkdir(parents=True)

            for url in spec.get("urls", []):
                filename = url.split("/")[-1]
                download(url, crd_dir / filename)

            yaml_files = list(crd_dir.glob("*.yaml")) + list(crd_dir.glob("*.yml"))
            if not yaml_files:
                raise FileNotFoundError(f"❌ No YAML files found for {name}")

            print(f"📥 Importing {name} CRDs to {schema_dir}")
            subprocess.run(
                ["kcl", "import", "-m", "crd", *map(str, yaml_files), "--output", str(schema_dir)],
                check=True,
            )


if __name__ == "__main__":
    fetch_crds()
