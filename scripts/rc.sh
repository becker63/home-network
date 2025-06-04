#!/usr/bin/env bash
set -euo pipefail

#
# 1) Overwrite src/lib/schema_interface.py to include:
#    - PROJECT_ROOT
#    - KFile(Generic[Dir]) with Generic imported
#    - ProjectSchema protocol
#
echo "✏️  Writing src/lib/schema_interface.py…"
cat > src/lib/schema_interface.py <<'EOF'
from typing import TypeVar, Generic, Protocol, Callable
from pathlib import Path
from enum import Enum, StrEnum
from pydantic import BaseModel, ConfigDict
from .find_proj_root import find_project_root

# === CONSTANT: PROJECT_ROOT only ===
PROJECT_ROOT: Path = find_project_root()

# === GENERIC KFile MODEL ===
Dir = TypeVar("Dir", bound=Enum)

class KFile(BaseModel, Generic[Dir]):
    model_config = ConfigDict(frozen=True)
    path: Path
    dirname: Dir

# === PROTOCOL: ProjectSchema Interface ===
Filter = TypeVar("Filter", bound=StrEnum)

class ProjectSchema(Protocol[Dir, Filter]):
    DirEnum: type[Dir]
    ProjectFilters: type[Filter]
    KFile: type[KFile[Dir]]

    def get_filters(self) -> dict[Filter, Callable[[object], bool]]:
        ...
EOF
echo "✅ src/lib/schema_interface.py written."

#
# 2) Overwrite src/schema_impl.py so it defines:
#    - PROJECT_ROOT (imported) & KCL_ROOT (computed)
#    - DirEnum
#    - ProjectFilters
#    - Bind generic KFile from interface to DirEnum
#    - MyProjectSchema implementing ProjectSchema
#
echo "✏️  Writing src/schema_impl.py…"
cat > src/schema_impl.py <<'EOF'
from pathlib import Path
from enum import Enum, StrEnum

# === Import PROJECT_ROOT & generic KFile from interface, then compute KCL_ROOT ===
from lib.schema_interface import PROJECT_ROOT, KFile
KCL_ROOT: Path = (PROJECT_ROOT / "kcl").resolve()

# === User-defined enums ===
class DirEnum(Enum):
    BOOTSTRAP  = "bootstrap"
    FRP_SCHEMA = "frp_schema"
    SCHEMAS    = "schemas"
    DEFAULT    = "default"

class ProjectFilters(StrEnum):
    BOOTSTRAP       = "bootstrap"
    BOOTSTRAP_SYNTH = "bootstrap_synth"
    RANDOM          = "random"

# === Concrete schema implementing the Protocol ===
from lib.schema_interface import ProjectSchema

class MyProjectSchema(ProjectSchema[DirEnum, ProjectFilters]):
    DirEnum = DirEnum
    ProjectFilters = ProjectFilters
    KFile = KFile[DirEnum]  # bind the generic to DirEnum

    def get_filters(self):
        return {
            ProjectFilters.BOOTSTRAP:        lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
            ProjectFilters.BOOTSTRAP_SYNTH:  lambda kf: kf.dirname == DirEnum.BOOTSTRAP,
            ProjectFilters.RANDOM:           lambda _kf: True,
        }
EOF
echo "✅ src/schema_impl.py written."

#
# 3) Overwrite src/lib/project_schema_runtime.py so it re-exports:
#    - PROJECT_ROOT, KCL_ROOT, DirEnum, ProjectFilters, KFile, FILTERS
#
echo "✏️  Writing src/lib/project_schema_runtime.py…"
cat > src/lib/project_schema_runtime.py <<'EOF'
from schema_impl import MyProjectSchema, DirEnum, ProjectFilters, KFile
from lib.schema_interface import PROJECT_ROOT
from schema_impl import KCL_ROOT

PROJECT_SCHEMA = MyProjectSchema()
FILTERS = PROJECT_SCHEMA.get_filters()
EOF
echo "✅ src/lib/project_schema_runtime.py written."

#
# 4) Patch src/lib/find_kcl_files.py so DirEnum and KCL_ROOT come from schema_impl
#
echo "🔧 Patching src/lib/find_kcl_files.py…"
awk '
  {
    line = $0
    # Replace DirEnum import
    gsub(/from +lib\.schema_interface +import +DirEnum/,        "from schema_impl import DirEnum", line)
    # Replace KCL_ROOT import
    gsub(/from +lib\.schema_interface +import +KCL_ROOT/,       "from schema_impl import KCL_ROOT", line)
    # Replace inline refs
    gsub(/lib\.schema_interface\.DirEnum/,   "schema_impl.DirEnum", line)
    gsub(/lib\.schema_interface\.KCL_ROOT/,  "schema_impl.KCL_ROOT", line)
    print line
  }
' src/lib/find_kcl_files.py > src/lib/find_kcl_files.tmp && mv src/lib/find_kcl_files.tmp src/lib/find_kcl_files.py
echo "✅ src/lib/find_kcl_files.py patched."

#
# 5) Patch all other .py files under src/ that reference project_context.* or schema_interface.KCL_ROOT
#
echo "🔁 Patching imports in remaining .py files under src/…"

find ./src -type f -name "*.py" | while read -r file; do
  [ -f "$file" ] || continue
  echo "Patching $file …"
  tmp="$(mktemp)"

  awk '
    {
      line = $0

      # Replace "from project_context import X"
      gsub(/from +project_context +import +DirEnum/,       "from schema_impl import DirEnum", line)
      gsub(/from +project_context +import +KFile/,         "from lib.schema_interface import KFile", line)
      gsub(/from +project_context +import +PROJECT_ROOT/,  "from lib.schema_interface import PROJECT_ROOT", line)
      gsub(/from +project_context +import +KCL_ROOT/,      "from schema_impl import KCL_ROOT", line)
      gsub(/from +project_context +import +ProjectFilters/,"from lib.project_schema_runtime import ProjectFilters", line)
      gsub(/from +project_context +import +FILTERS/,       "from lib.project_schema_runtime import FILTERS", line)

      # Handle comma-separated imports in one line
      gsub(/from +project_context +import +PROJECT_ROOT *, *KCL_ROOT/, "from lib.schema_interface import PROJECT_ROOT\nfrom schema_impl import KCL_ROOT", line)
      gsub(/from +project_context +import +PROJECT_ROOT *, *DirEnum/,  "from lib.schema_interface import PROJECT_ROOT\nfrom schema_impl import DirEnum", line)
      gsub(/from +project_context +import +DirEnum *, *KFile/,         "from schema_impl import DirEnum\nfrom lib.schema_interface import KFile", line)
      gsub(/from +project_context +import +ProjectFilters *, *FILTERS/,"from lib.project_schema_runtime import ProjectFilters\nfrom lib.project_schema_runtime import FILTERS", line)

      # Replace inline "lib.schema_interface.KCL_ROOT" → "schema_impl.KCL_ROOT"
      gsub(/lib\.schema_interface\.KCL_ROOT/, "schema_impl.KCL_ROOT", line)
      # Replace inline "project_context.KCL_ROOT"
      gsub(/project_context\.KCL_ROOT/,      "schema_impl.KCL_ROOT", line)

      print line
    }
  ' "$file" > "$tmp" && mv "$tmp" "$file"
done

echo "✅ All imports patched."
echo "📝 You can now delete src/project_context.py if no longer needed."
