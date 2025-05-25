# ========================================
# 📌 Provider Versions & Sources

# Static CRD versions (used with doc.crds.dev)
CROSSPLANE_VERSION := "v1.19.1"
PROVIDER_HELM_VERSION := "v0.15.0"
PATCH_FN_VERSION := "v0.7.0"

# Upjet-based providers (Git submodules, name=url)
UPJET_PROVIDERS := "provider-cloudflare=https://github.com/cdloh/provider-cloudflare provider-proxmoxve=https://github.com/dougsong/provider-proxmoxve"

# ========================================
# 🔧 Base Commands (Hidden)

_default: _help

_help:
    @just --list

# ========================================
# 🧱 Build & Test Flow

compile:
    rm -rf dist && bunx tsc --build

synth:
    bunx cdk8s synth

generate:
    bun run scripts/generate-kuttl-tests.ts

test:
    kubectl kuttl test ./kuttl_tests

clean:
    rm -rf ./synth_yaml/*

all:
    just clean
    just compile
    just synth
    just generate
    just test

build:
    just clean
    just compile
    just synth
    just generate

# ========================================
# 📦 CRD Sources: Prebuilt & Upjet

download-crds:
    mkdir -p crds
    curl -L https://doc.crds.dev/raw/github.com/crossplane/crossplane@{{CROSSPLANE_VERSION}} \
        -o crds/crossplane-core.yaml
    curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/provider-helm@{{PROVIDER_HELM_VERSION}} \
        -o crds/provider-helm.yaml
    curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/function-patch-and-transform@{{PATCH_FN_VERSION}} \
        -o crds/function-patch-transform.yaml

importcrds:
    bun run scripts/import-crds.ts

build-cloudflare:
    bun run scripts/upjet-make.ts crossplane-providers/provider-cloudflare

build-proxmoxve:
    bun run scripts/upjet-make.ts crossplane-providers/provider-proxmoxve

build-upjet-providers:
    just build-cloudflare
    just build-proxmoxve

add-upjet-provider-submodules:
    mkdir -p crossplane-providers
    bun run scripts/add-upjet-submodules.ts {{UPJET_PROVIDERS}}

# ========================================
# 🔄 CRD Sync & Automation

fetch-imports:
    @echo "\033[0;31mThis must be run in the dev-upjet env!\033[0m"
    just add-upjet-provider-submodules
    just download-crds
    just build-upjet-providers
    just importcrds

# ========================================
# 🧪 Development Environments

dev-main:
    nix develop .#default

dev-upjet:
    nix develop .#upjet-env

# ========================================
# 🧾 Info / Debug

print-provider-versions:
    @echo "Static CRD Versions:"
    @echo "  crossplane:              {{CROSSPLANE_VERSION}}"
    @echo "  provider-helm:           {{PROVIDER_HELM_VERSION}}"
    @echo "  function-patch-transform:{{PATCH_FN_VERSION}}"
    @echo
    @echo "Upjet Providers:"
    @echo "  {{UPJET_PROVIDERS}}"
