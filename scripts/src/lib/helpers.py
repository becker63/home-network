from pathlib import Path

def find_project_root() -> Path:
    current = Path(__file__).resolve()
    markers = ["flake.nix", ".git"]

    while True:
        if any((current / marker).exists() for marker in markers):
            return current
        if current.parent == current:
            raise RuntimeError(f"Could not find project root. Missing any of: {markers}")
        current = current.parent
