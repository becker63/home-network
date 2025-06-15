#!/usr/bin/env python3

import subprocess
import json
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any, cast
from urllib.request import urlretrieve
from genson import SchemaBuilder
from configuration import HELM_VALUES, SCHEMA_ROOT


def yaml_to_json_schema(yaml_path: Path) -> Dict[str, Any]:
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    builder = SchemaBuilder()
    builder.add_object(data)  # pyright: ignore[reportUnknownMemberType]
    return cast(Dict[str, Any], builder.to_schema())


def fetch_helm_values() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        for name, conf in HELM_VALUES.items():
            print(f"\n📦 Fetching {name} Helm values.yaml")

            kcl_output_file = SCHEMA_ROOT / name / "schema.k"
            kcl_output_file.parent.mkdir(parents=True, exist_ok=True)

            for url in conf.get("urls", []):
                values_path = tmp_path / f"{name}.values.yaml"
                schema_path = tmp_path / f"{name}.values.schema.json"

                print(f"  ↳ Downloading: {url}")
                urlretrieve(url, values_path)

                print("🔁 Generating JSON Schema")
                schema = yaml_to_json_schema(values_path)
                with schema_path.open("w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2)

                print(f"📥 Importing to KCL: {kcl_output_file}")
                subprocess.run(
                    ["kcl", "import", "-m", "jsonschema", str(schema_path), "--output", str(kcl_output_file), "--force"],
                    check=True,
                )


if __name__ == "__main__":
    fetch_helm_values()
