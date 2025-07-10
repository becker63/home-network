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

        for schema in CRD_SPECS:
            print(f"\n📦 Fetching {schema.name} CRDs...")
            schema_dir = SCHEMA_ROOT / schema.name
            schema_dir.mkdir(parents=True, exist_ok=True)

            crd_dir = tmp_path / schema.name
            crd_dir.mkdir(parents=True)

            for url in schema.urls:
                filename = url.split("/")[-1]
                download(url, crd_dir / filename)

            yaml_files = list(crd_dir.glob("*.yaml")) + list(crd_dir.glob("*.yml"))
            if not yaml_files:
                raise FileNotFoundError(f"❌ No YAML files found for {schema.name}")

            print(f"📥 Importing {schema.name} CRDs to {schema_dir}")
            subprocess.run(
                ["kcl", "import", "-m", "crd", *map(str, yaml_files), "--output", str(schema_dir)],
                check=True,
            )


if __name__ == "__main__":
    fetch_crds()
