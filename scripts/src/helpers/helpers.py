import subprocess


class CommandError(Exception):
    def __init__(self, extra_info: str | None = None):
        super().__init__()
        self.__rich_info__ = extra_info

    def __str__(self) -> str:
        return "your command broke dawg"

def run_command(cmd: list[str], kf_name: str | None = None) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise CommandError(
            extra_info=e.stderr.strip() or e.stdout.strip() or "No stderr or stdout output"
        ) from e
