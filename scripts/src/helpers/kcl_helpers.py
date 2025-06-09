from configuration import KFile
from pathlib import Path
from threading import Lock
from typing import Optional, Any
from enum import Enum, auto
import kcl_lib.api as bapi
from kcl_lib.api import UpdateDependencies_Args, ExecProgram_Result
from configuration import KCL_ROOT

# Thread safe kcl api singleton with our deps
class KCLContext:
    _instance: Optional["KCLContext"] = None
    _lock: Lock = Lock()

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.api: bapi.API = bapi.API()

        deps_args: UpdateDependencies_Args = UpdateDependencies_Args(manifest_path=str(KCL_ROOT))
        deps_result = self.api.update_dependencies(deps_args)
        self.external_pkgs: Any = deps_result.external_pkgs  # Replace 'Any' with the actual type if known

        self._initialized = True

    @classmethod
    def instance(cls) -> "KCLContext":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = cls()
        return cls._instance


def Exec(path: Path) -> ExecProgram_Result:
    ctx = KCLContext.instance()

    exec_args = bapi.ExecProgram_Args(
        k_filename_list=[str(path)],
        external_pkgs=ctx.external_pkgs
    )

    return ctx.api.exec_program(exec_args)

class FRPTYPE(Enum):
    FRPC = auto()
    FRPS = auto()
    DAEMONSET = auto()
    NONE = auto()


def kcl_path_to_frp_relevant(kf: KFile, outfile: Path) -> FRPTYPE:
    args = bapi.ParseFile_Args(path=str(kf.path))
    api = bapi.API()
    result = api.parse_file(args).ast_json

    # TODO: actually parse the ast for manifests.yaml_stream(...) to get the list of exported types to iterate through
    if "ClientConfig" in result:
        return FRPTYPE.FRPC
    if "ServerConfig" in result:
        return FRPTYPE.FRPS
    if "DaemonSet" in result:
        return FRPTYPE.DAEMONSET

    return FRPTYPE.NONE
