# KCL Project Automation Justfile

# ────────────────
# Import CRDs via KCL modules
# ────────────────
[working-directory: "kcl"]
import-crds:
    kcl mod add external-secrets:0.1.4
    kcl mod add argo-cd:0.2.1
    kcl mod add fluxcd-helm-controller:v1.0.3
    kcl mod add fluxcd:0.1.2
    kcl mod add cert-manager:0.3.0
    kcl mod add crossplane:1.17.3
    kcl mod add fluxcd-source-controller:v1.3.2
    kcl mod add crossplane-provider-gcp:0.22.2

# ────────────────
# Generate Go-based KCL schemas
# ────────────────
[working-directory: "kcl/schemas/go"]
gen-go-schema:
    go run schema-gen.go

# ────────────────
# Full environment setup
# ────────────────
all:
    just import-crds
    just gen-go-schema
    fetch_helm_values
    fetch_crds

# ────────────────
# Git commit shortcut
# ────────────────
[working-directory: "."]
git-commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"
    git push

# ────────────────
# Run tests with optional filter
# ────────────────
[working-directory: "scripts"]
[no-exit-message]
test K_EXPRESSION="":
    @bash -c 'if [ "{{K_EXPRESSION}}" = "" ]; then pytest; else pytest -k "{{K_EXPRESSION}}"; fi'
