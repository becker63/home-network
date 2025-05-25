#!/usr/bin/env bash
set -euo pipefail

PATCHED_PROVIDERS=(
  "crossplane-providers/provider-cloudflare"
  "crossplane-providers/provider-proxmoxve"
)

for PROVIDER in "${PATCHED_PROVIDERS[@]}"; do
  echo "🔧 Patching $PROVIDER/Makefile..."

  # Remove any Terraform installation logic (we're using system one)
  sed -i.bak '/@curl -fsSL .*terraform.*zip/d' "$PROVIDER/Makefile"
  sed -i.bak '/@unzip .*terraform.*zip/d' "$PROVIDER/Makefile"
  sed -i.bak '/@mv .*terraform /d' "$PROVIDER/Makefile"
  sed -i.bak '/@rm -fr .*tmp-terraform/d' "$PROVIDER/Makefile"
  sed -i.bak '/@mkdir -p .*tmp-terraform/d' "$PROVIDER/Makefile"
  sed -i.bak '/@$(OK) installing terraform .*/d' "$PROVIDER/Makefile"
  sed -i.bak '/@$(INFO) installing terraform .*/d' "$PROVIDER/Makefile"

  # Replace custom terraform path with system terraform
  sed -i.bak 's|$(TOOLS_HOST_DIR)/terraform-$(TERRAFORM_VERSION)|terraform|g' "$PROVIDER/Makefile"
  sed -i.bak 's|$(TERRAFORM)|terraform|g' "$PROVIDER/Makefile"

  rm "$PROVIDER/Makefile.bak"
done

echo "✅ Done patching Makefiles to use system Terraform"
