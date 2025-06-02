# Justfile for managing KCL projects and testing

CRD_DIR := "crds/kuttl"

# ─────────────────────────────
# CRD Imports (infra/)
# ─────────────────────────────
[working-directory: "kcl"]
import-crds:
    kcl mod add sealed-secrets:v0.27.2
    kcl mod add argo-cd:0.2.1
    kcl mod add cert-manager:0.3.0
    kcl mod add crossplane:1.17.3

# ─────────────────────────────
# Schema Generation (infra/schemas/go)
# ─────────────────────────────
[working-directory: "kcl/schemas/go/"]
gen-go-schema:
    go run schema-gen.go

# ─────────────────────────────
# KUTTL CRDs Download & Import
# ─────────────────────────────
[working-directory: "kcl"]
download-kuttl-crds:
    mkdir -p {{CRD_DIR}}
    curl -fsSL -o {{CRD_DIR}}/testassert_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml &
    curl -fsSL -o {{CRD_DIR}}/teststep_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml &
    curl -fsSL -o {{CRD_DIR}}/testsuite_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml &
    wait

[working-directory: "kcl"]
import-kuttl-crds:
    kcl import -m crd {{CRD_DIR}}/*.yaml --output schemas/kuttl

# ─────────────────────────────
# Full Setup: all schemas and CRDs
# ─────────────────────────────
all:
    @echo -e "\033[1;34m==> Importing infra CRDs...\033[0m"
    just import-crds
    @echo -e "\033[1;32m==> Generating FRP schema...\033[0m"
    just gen-go-schema
    @echo -e "\033[1;33m==> Downloading KUTTL CRDs...\033[0m"
    just download-kuttl-crds
    @echo -e "\033[1;35m==> Importing KUTTL CRDs...\033[0m"
    just import-kuttl-crds

# ─────────────────────────────
# Git Commands
# ─────────────────────────────
[working-directory: "."]
git-commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"
    git push

# ─────────────────────────────
# Pytest with optional -k expression
# Runs tests in 'scripts' directory
# ─────────────────────────────
[working-directory: "scripts"]
[no-exit-message] # hide justs distracting output, but keep the exit code
test K_EXPRESSION="":
    @bash -c 'if [ "{{K_EXPRESSION}}" = "" ]; then pytest; else pytest -k "{{K_EXPRESSION}}"; fi'
