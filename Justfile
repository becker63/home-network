# _Hidden
_default: _help

_help:
	@just --list

# 0. Compile ts
compile:
	rm -rf dist && bunx tsc --build

# 1. Generate Kubernetes YAML
synth:
	bunx cdk8s synth

# 2. Generate KUTTL files
generate:
	bun run scripts/generate-kuttl-tests.ts

# 3. Run unit tests on charts (must fill in asserts first)
test:
	kubectl kuttl test ./kuttl_tests

# Clean up synth_yaml
clean:
	rm -rf ./synth_yaml/*

# 0–3. Full build & test cycle
all:
	just clean
	just compile
	just synth
	just generate
	just test

# 0–3. Full rebuild (TODO: rethink the file synth hashes maybe? So Argo doesn't reapply all the time)
build:
	just clean
	just compile
	just synth
	just generate

# get the crds for each of these
download-crds:
	mkdir -p crds
	curl -L https://doc.crds.dev/raw/github.com/crossplane/crossplane@`bun run scripts/get-version.ts CROSSPLANE_VERSION` \
		-o crds/crossplane-core.yaml
	curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/provider-helm@`bun run scripts/get-version.ts PROVIDER_HELM_VERSION` \
		-o crds/provider-helm.yaml
	curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/function-patch-and-transform@`bun run scripts/get-version.ts PATCH_FN_VERSION` \
		-o crds/function-patch-transform.yaml

# Import those CRDs into CDK8s with explicit names
importcrds:
	bun run scripts/import-crds.ts

fetch-imports:
	just download-crds
	just importcrds

# Build provider-cloudflare
build-cloudflare:
	bun run scripts/upjet-make.ts crossplane-providers/provider-cloudflare

# Build provider-proxmoxve
build-proxmoxve:
	bun run scripts/upjet-make.ts crossplane-providers/provider-proxmoxve


# ================================
# Dev environments

# Launch main dev environment
dev-main:
	nix develop .#default

# Launch Upjet provider dev environment (Go 1.19, Terraform)
dev-upjet:
	nix develop .#upjet-env
