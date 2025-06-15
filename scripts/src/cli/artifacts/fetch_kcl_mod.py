#!/usr/bin/env python3

import subprocess
from configuration import KCL_ROOT, KCL_IMPORTS

def add_kcl_deps() -> None:
    for module, version in KCL_IMPORTS.items():
        print(f"📦 Adding {module}:{version}")
        try:
            subprocess.run(
                ["kcl", "mod", "add", f"{module}:{version}"],
                cwd=KCL_ROOT,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"❌ Failed to add {module}:{version}: {e}") from e

if __name__ == "__main__":
    add_kcl_deps()
