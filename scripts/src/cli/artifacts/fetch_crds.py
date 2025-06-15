import subprocess
import urllib.request
from pathlib import Path
from configuration import CRD_SPECS, CRD_ROOT, SCHEMA_ROOT

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def download(url: str, dest: Path) -> None:
    print(f"📥 Downloading {url}")
    try:
        with urllib.request.urlopen(url) as response:
            dest.write_bytes(response.read())
    except Exception as e:
        raise RuntimeError(f"❌ Failed to download {url}: {e}")

def fetch_crds() -> None:
    for name, spec in CRD_SPECS.items():
        print(f"\n📦 Fetching {name} CRDs...")
        crd_dir = CRD_ROOT / name
        schema_dir = SCHEMA_ROOT / name
        ensure_dir(crd_dir)
        ensure_dir(schema_dir)

        for url in spec.get("urls", []):
            filename = url.split("/")[-1]
            download(url, crd_dir / filename)

        yaml_files = list(crd_dir.glob("*.yaml")) + list(crd_dir.glob("*.yml"))
        if not yaml_files:
            raise FileNotFoundError(f"❌ No YAML files found in {crd_dir}")

        print(f"📥 Importing {name} CRDs to {schema_dir}")
        subprocess.run(
            ["kcl", "import", "-m", "crd", *map(str, yaml_files), "--output", str(schema_dir)],
            check=True
        )

if __name__ == "__main__":
    fetch_crds()
