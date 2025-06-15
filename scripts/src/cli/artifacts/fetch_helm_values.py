#!/usr/bin/env python3

import subprocess
import json
import yaml
from genson import SchemaBuilder
from urllib.request import urlretrieve
from pathlib import Path
from typing import Dict, List, Any, cast
from configuration import PROJECT_ROOT


HELM_VALUES: Dict[str, Dict[str, List[str]]] = {
    "oauth2-proxy": {
        "urls": [
            "https://raw.githubusercontent.com/oauth2-proxy/manifests/main/helm/oauth2-proxy/values.yaml"
        ]
    },
    # Add more charts here
}


def yaml_to_json_schema(yaml_path: Path) -> Dict[str, Any]:
    with yaml_path.open("r", encoding="utf-8") as f:
        yaml_data: Any = yaml.safe_load(f)

    builder: SchemaBuilder = SchemaBuilder()
    builder.add_object(yaml_data) # pyright: ignore[reportUnknownMemberType]
    schema = cast(Dict[str, Any], builder.to_schema())
    return schema


def fetch_and_generate() -> None:
    for name, conf in HELM_VALUES.items():
        urls: List[str] = conf.get("urls", [])
        chart_dir: Path = PROJECT_ROOT / "kcl" / "schemas" / "helm_values" / name
        kcl_schema_dir: Path = PROJECT_ROOT / "kcl" / "schemas" / name

        chart_dir.mkdir(parents=True, exist_ok=True)
        kcl_schema_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 Fetching {name} Helm values.yaml")

        for url in urls:
            values_path: Path = chart_dir / "values.yaml"
            schema_path: Path = chart_dir / "values.schema.json"

            print(f"  ↳ Downloading: {url}")
            urlretrieve(url, values_path)

            print("🔁 Generating JSON Schema from values.yaml")
            schema: Dict[str, Any] = yaml_to_json_schema(values_path)
            with schema_path.open("w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)

            output_file = kcl_schema_dir / "schema.k"

            print(f"📥 Importing to KCL schema file: {output_file}")
            subprocess.run([
                "kcl", "import", "-m", "jsonschema",
                str(schema_path),
                "--output", str(output_file),
                "--force"
            ], check=True)


if __name__ == "__main__":
    fetch_and_generate()
