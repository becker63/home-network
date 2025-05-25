#!/usr/bin/env bash
set -euo pipefail

export SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.txt}"

for file in "$@"; do
  if [ -f "$file" ]; then
    echo "🔓 Decrypting $file with sops..."
    sops -d --output "$file" "$file" || echo "⚠️  Warning: $file decryption failed"
  else
    echo "⚠️  Skipping missing file: $file"
  fi
done
