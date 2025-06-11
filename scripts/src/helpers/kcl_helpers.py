from contextlib import contextmanager
from typing import Generator, Mapping
from pathlib import Path
import shutil

from kcl_lib.api.spec_pb2 import OverrideFile_Result
from kcl_lib import api as bapi
from configuration import KCL_ROOT
from threading import Lock
from typing import Optional, Any
from kcl_lib.api import UpdateDependencies_Args, ExecProgram_Result
from google.protobuf.json_format import MessageToDict

# === KCL Context Singleton ===

class KCLContext:
    _instance: Optional["KCLContext"] = None
    _lock: Lock = Lock()

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.api: bapi.API = bapi.API()
        deps_args = UpdateDependencies_Args(manifest_path=str(KCL_ROOT))
        deps_result = self.api.update_dependencies(deps_args)
        self.external_pkgs = deps_result.external_pkgs
        self._initialized = True

    @classmethod
    def instance(cls) -> "KCLContext":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

# === Execution Helpers ===

def Exec(path: Path) -> ExecProgram_Result:
    ctx = KCLContext.instance()
    exec_args = bapi.ExecProgram_Args(
        k_filename_list=[str(path.absolute())],
        external_pkgs=ctx.external_pkgs
    )
    result = ctx.api.exec_program(exec_args)
    if result.err_message:
        raise RuntimeError(f"KCL execution failed:\n{result.err_message}")
    return result

def Override(path: Path, specs: list[str]) -> OverrideFile_Result:
    ctx = KCLContext.instance()
    return ctx.api.override_file(bapi.OverrideFile_Args(
        file=str(path.absolute()), specs=specs
    ))

@contextmanager
def Override_file_tmp_multi(
    overrides: Mapping[Path, list[str]]
) -> Generator[dict[Path, OverrideFile_Result], None, None]:
    backups: dict[Path, Path] = {}
    for path in overrides:
        backup: Path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        backups[path] = backup

    try:
        results: dict[Path, OverrideFile_Result] = {
            path: Override(path, specs) for path, specs in overrides.items()
        }
        yield results
    finally:
        for path, backup in backups.items():
            shutil.move(backup, path)

def ListVariables(path: Path) -> dict[str, Any]:
    ctx = KCLContext.instance()
    args = bapi.ListVariables_Args(files=[str(path)])
    return MessageToDict(ctx.api.list_variables(args))
