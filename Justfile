# Justfile for managing KCL projects and testing

# ─────────────────────────────
# Paths for CRDs and Schema Output
# ─────────────────────────────
KUTTL_CRD_DIR := "crds/kuttl"
KUTTL_SCHEMA_DIR := "schemas/kuttl"

INFISICAL_CRD_DIR := "crds/infisical"
INFISICAL_SCHEMA_DIR := "schemas/infisical"

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
[working-directory: "kcl/schemas/go"]
gen-go-schema:
    go run schema-gen.go

# ─────────────────────────────
# Import KUTTL CRDs
# ─────────────────────────────
[working-directory: "kcl"]
import-kuttl-crds:
    mkdir -p {{KUTTL_CRD_DIR}} {{KUTTL_SCHEMA_DIR}}
    curl -fsSL -o {{KUTTL_CRD_DIR}}/testassert_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml
    curl -fsSL -o {{KUTTL_CRD_DIR}}/teststep_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml
    curl -fsSL -o {{KUTTL_CRD_DIR}}/testsuite_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml
    kcl import -m crd {{KUTTL_CRD_DIR}}/*.yaml --output {{KUTTL_SCHEMA_DIR}}

# ─────────────────────────────
# Import Infisical CRDs
# ─────────────────────────────
[working-directory: "kcl"]
import-infisical-crds:
    mkdir -p {{INFISICAL_CRD_DIR}} {{INFISICAL_SCHEMA_DIR}}
    curl -fsSL -o {{INFISICAL_CRD_DIR}}/infisicaldynamicsecret_crd.yaml https://raw.githubusercontent.com/Infisical/infisical/refs/heads/main/k8-operator/config/crd/bases/secrets.infisical.com_infisicaldynamicsecrets.yaml
    kcl import -m crd {{INFISICAL_CRD_DIR}}/*.yaml --output {{INFISICAL_SCHEMA_DIR}}

# ─────────────────────────────
# Import All CRDs (modular)
# ─────────────────────────────
import-all-crds: import-kuttl-crds import-infisical-crds

# ─────────────────────────────
# Full Setup: all schemas and CRDs
# ─────────────────────────────
all: import-crds gen-go-schema import-all-crds

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
# ─────────────────────────────
[working-directory: "scripts"]
[no-exit-message]
test K_EXPRESSION="":
    @bash -c 'if [ "{{K_EXPRESSION}}" = "" ]; then pytest; else pytest -k "{{K_EXPRESSION}}"; fi'