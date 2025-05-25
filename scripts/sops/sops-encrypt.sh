#!/usr/bin/env bash
set -euo pipefail

export SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.txt}"

for file in "$@"; do
  if [ -f "$file" ]; then
    if grep -q '"sops":' "$file"; then
      echo "🔐 Skipping already-encrypted file: $file"
    else
      echo "🔐 Encrypting $file with sops..."
      sops -e --in-place "$file"
    fi
  else
    echo "⚠️  Skipping missing file: $file"
  fi
done
