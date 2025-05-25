# ========================================
# 📌 Provider Versions & Sources

CROSSPLANE_VERSION := "v1.19.1"
PROVIDER_HELM_VERSION := "v0.15.0"
PATCH_FN_VERSION := "v0.7.0"
ARGOCD_VERSION := "v2.10.7"

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

generate-tests:
    bun run scripts/generate-kuttl-tests.ts

test:
    kubectl kuttl test --config kuttl-test.yaml

# dont touch me..
test-one test:
    bash -c 'test_dir="$(basename {{test}})"; echo "Running: kubectl kuttl test --config kuttl-test.yaml --test $test_dir"; kubectl kuttl test --config kuttl-test.yaml --test "$test_dir"'


clean:
    rm -rf ./synth_yaml/*

all:
    just clean
    just compile
    just synth
    just generate-tests
    just test

build:
    just clean
    just compile
    just synth
    just generate-tests

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
    curl -L https://raw.githubusercontent.com/argoproj/argo-cd/{{ARGOCD_VERSION}}/manifests/crds/application-crd.yaml \
        -o crds/argocd-application.yaml
    curl -L https://raw.githubusercontent.com/argoproj/argo-cd/{{ARGOCD_VERSION}}/manifests/crds/appproject-crd.yaml \
        -o crds/argocd-appproject.yaml

importcrds:
    bun run scripts/import-crds.ts

build-cloudflare:
    bun run scripts/upjet-make.ts crossplane-providers/provider-cloudflare

build-proxmoxve:
    bun run  scripts/upjet-make.ts crossplane-providers/provider-proxmoxve

build-upjet-providers:
    just build-cloudflare
    just build-proxmoxve

# ========================================
# 🔄 CRD Sync & Automation

fetch-imports:
	nix develop .#upjet-env --command bash -c '\
		set -euo pipefail; \
		echo "🔁 Updating submodules..."; \
		git submodule update --init --recursive; \
		echo "🔧 Patching provider Makefiles..."; \
		./scripts/patch-providers.sh; \
		echo "📥 Downloading CRDs..."; \
		just download-crds; \
		echo "🔨 Building patched providers..."; \
		just build-upjet-providers; \
		echo "📦 Importing CRDs..."; \
		just importcrds; \
		echo "🚀 Applying CRDs to the cluster..."; \
		kubectl apply -f ./crds;'

# ========================================
# 🧪 Development Environments

dev-main:
    nix develop .#default

dev-upjet:
    nix develop .#upjet-env

decrypt-secrets:
    ./scripts/sops/sops-decrypt.sh secrets.json
