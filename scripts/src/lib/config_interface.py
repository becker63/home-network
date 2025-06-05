# src/lib/runtime_config.py

from configuration import (
    KFile,
    KCL_ROOT,
    DirEnum,
    ProjectFilters,
    FILTERS,
    PROJECT_ROOT
)

assert hasattr(DirEnum, "DEFAULT"), "DirEnum must define DEFAULT"
assert hasattr(ProjectFilters, "DEFAULT"), "ProjectFilters must define DEFAULT"

__all__ = [
    "PROJECT_ROOT",
    "KCL_ROOT",
    "DirEnum",
    "ProjectFilters",
    "KFile",
    "FILTERS",
]
