from lib.config_interface import PROJECT_ROOT
from configuration import KCL_ROOT
from configuration import DirEnum, ProjectFilters, KFile
from configuration import MyProjectSchema

PROJECT_SCHEMA = MyProjectSchema()
FILTERS = PROJECT_SCHEMA.get_filters()

# Re-export all for lib consumers:
__all__ = [
    "PROJECT_ROOT",
    "KCL_ROOT",
    "DirEnum",
    "ProjectFilters",
    "KFile",
    "FILTERS",
]
