# Justfile for managing KCL projects and testing

CRD_DIR := "crds/kuttl"

# ─────────────────────────────
# CRD Imports (infra/)
# ─────────────────────────────
[working-directory: "kcl"]
import-crds:
    if ! grep -q sealed-secrets kcl.mod 2>/dev/null; then \
      kcl mod add sealed-secrets:v0.27.2; \
    fi
    if ! grep -q argo-cd kcl.mod 2>/dev/null; then \
      kcl mod add argo-cd:0.2.1; \
    fi
    if ! grep -q cert-manager kcl.mod 2>/dev/null; then \
      kcl mod add cert-manager:0.3.0; \
    fi
    if ! grep -q crossplane kcl.mod 2>/dev/null; then \
      kcl mod add crossplane:1.17.3; \
    fi

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
    if [ ! -f {{CRD_DIR}}/testassert_crd.yaml ]; then \
      curl -fsSL -o {{CRD_DIR}}/testassert_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml; \
    fi
    if [ ! -f {{CRD_DIR}}/teststep_crd.yaml ]; then \
      curl -fsSL -o {{CRD_DIR}}/teststep_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml; \
    fi
    if [ ! -f {{CRD_DIR}}/testsuite_crd.yaml ]; then \
      curl -fsSL -o {{CRD_DIR}}/testsuite_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml; \
    fi

[working-directory: "kcl"]
import-kuttl-crds: download-kuttl-crds
    files=$(find crds/kuttl -name '*.yaml') && \
    [ -n "$files" ] && kcl import -m crd $files --output schemas/kuttl || \
    (echo "❌ No CRD YAMLs found in crds/kuttl"; exit 1)

# ─────────────────────────────
# Full Setup: all schemas and CRDs
# ─────────────────────────────
all: import-crds gen-go-schema import-kuttl-crds

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
[no-exit-message]
test K_EXPRESSION="":
    @bash -c 'if [ "{{K_EXPRESSION}}" = "" ]; then pytest; else pytest -k "{{K_EXPRESSION}}"; fi'
