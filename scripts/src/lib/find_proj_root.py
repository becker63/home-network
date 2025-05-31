from pathlib import Path

def find_project_root() -> Path:
    current = Path(__file__).resolve()
    while True:
        if (current / "flake.nix").exists():
            return current
        if current.parent == current:
            raise RuntimeError("Could not find project root (missing flake.nix)")
        current = current.parent
