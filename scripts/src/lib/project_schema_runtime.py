from schema_impl import MyProjectSchema, DirEnum, ProjectFilters, KFile
from lib.schema_interface import PROJECT_ROOT
from schema_impl import KCL_ROOT

PROJECT_SCHEMA = MyProjectSchema()
FILTERS = PROJECT_SCHEMA.get_filters()
