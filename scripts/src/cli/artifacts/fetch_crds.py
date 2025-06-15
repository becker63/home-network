#!/usr/bin/env python3

import subprocess
from urllib.request import urlretrieve
from configuration import PROJECT_ROOT

CRDS = {
    "kuttl": {
        "urls": [
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml",
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml",
            "https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml",
        ]
    },
    "traefik": {
        "urls": [
            "https://raw.githubusercontent.com/traefik/traefik/refs/heads/v3.4/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml"
        ]
    },
}

def fetch_crds():
    for name, conf in CRDS.items():
        crd_dir = PROJECT_ROOT / "kcl" / "crds" / name
        schema_dir = PROJECT_ROOT / "kcl" / "schemas" / name
        crd_dir.mkdir(parents=True, exist_ok=True)
        schema_dir.mkdir(parents=True, exist_ok=True)

        print(f"📦 Fetching {name} CRDs...")
        for url in conf["urls"]:
            target = crd_dir / url.split("/")[-1]
            print(f"  ↳ Downloading {url}")
            urlretrieve(url, target)

        print(f"📥 Importing {name} CRDs to {schema_dir}")

        command = f'kcl import -m crd {crd_dir}/*.yaml --output {schema_dir}'
        subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":
    fetch_crds()
