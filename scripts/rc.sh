#!/usr/bin/env bash
set -euo pipefail

echo "1️⃣  Renaming files…"

# Rename schema_interface → config_interface
if [ -f "src/lib/schema_interface.py" ]; then
  mv src/lib/schema_interface.py src/lib/config_interface.py
  echo "   ✅ Renamed schema_interface.py → config_interface.py"
else
  echo "   ⚠️  src/lib/schema_interface.py not found; skipping"
fi

# Rename project_schema_runtime → runtime_config
if [ -f "src/lib/project_schema_runtime.py" ]; then
  mv src/lib/project_schema_runtime.py src/lib/runtime_config.py
  echo "   ✅ Renamed project_schema_runtime.py → runtime_config.py"
else
  echo "   ⚠️  src/lib/project_schema_runtime.py not found; skipping"
fi

echo
echo "2️⃣  Patching imports in all .py files under src/…"

find ./src -type f -name "*.py" | while read -r file; do
  [ -f "$file" ] || continue
  echo "   Patching $file"
  tmp="$(mktemp)"

  awk '
    {
      line = $0

      # Replace any "from lib.schema_interface import X" → "from lib.config_interface import X"
      gsub(/from +lib\.schema_interface +import/,    "from lib.config_interface import", line)
      # Replace any inline "lib.schema_interface.X" → "lib.config_interface.X"
      gsub(/lib\.schema_interface\./,                "lib.config_interface.",    line)

      # Replace any "from lib.project_schema_runtime import X" → "from lib.runtime_config import X"
      gsub(/from +lib\.project_schema_runtime +import/,    "from lib.runtime_config import", line)
      # Replace any inline "lib.project_schema_runtime.X" → "lib.runtime_config.X"
      gsub(/lib\.project_schema_runtime\./,                  "lib.runtime_config.",        line)

      print line
    }
  ' "$file" > "$tmp" && mv "$tmp" "$file"
done

echo "   ✅ Import patching complete."
echo
echo "✅ All done. Your modules now import from 'lib.config_interface' and 'lib.runtime_config'."
