from threading import Lock
from pathlib import Path

from kcl_lib import api
from kcl_lib.api import UpdateDependencies_Args

from config.base import KCL_ROOT


# Thread safe kcl api singleton with our deps
class KCLContext:
    _instance: "KCLContext | None" = None
    _lock: Lock = Lock()

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.api: api.API = api.API()

        deps_args = UpdateDependencies_Args(manifest_path=str(KCL_ROOT))
        deps_result = self.api.update_dependencies(deps_args)
        self.external_pkgs = deps_result.external_pkgs

        self._initialized = True

    @classmethod
    def instance(cls) -> "KCLContext":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = cls()
        return cls._instance

def Exec(path: Path):
    ctx = KCLContext.instance()

    exec_args = api.ExecProgram_Args(
        k_filename_list=[str(path)],
            external_pkgs=ctx.external_pkgs
    )

    return ctx.api.exec_program(exec_args)
