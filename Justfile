CRD_DIR := "crds/kuttl"

# CRD imports (infra/)
[working-directory: "infra"]
import-crds:
    kcl mod add sealed-secrets:v0.27.2
    kcl mod add argo-cd:0.2.1
    kcl mod add cert-manager:0.3.0
    kcl mod add crossplane:1.17.3

# Schema generation (infra/schemas/frp_schema)
[working-directory: "infra/schemas/frp_schema"]
gen-frp-schema:
    go run gen-schema.go

# KUTTL CRDs (kuttl-tests/)
[working-directory: "kuttl-tests"]
download-kuttl-crds:
    mkdir -p {{CRD_DIR}}
    curl -fsSL -o {{CRD_DIR}}/testassert_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testassert_crd.yaml &
    curl -fsSL -o {{CRD_DIR}}/teststep_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/teststep_crd.yaml &
    curl -fsSL -o {{CRD_DIR}}/testsuite_crd.yaml https://raw.githubusercontent.com/kudobuilder/kuttl/refs/heads/main/crds/testsuite_crd.yaml &
    wait

[working-directory: "kuttl-tests"]
import-kuttl-crds:
    kcl import -m crd ../{{CRD_DIR}}/*.yaml --output schema

# sets up all schemas and CRDs
all:
    @echo -e "\033[1;34m==> Importing infra CRDs...\033[0m"
    just import-crds
    @echo -e "\033[1;32m==> Generating FRP schema...\033[0m"
    just gen-frp-schema
    @echo -e "\033[1;33m==> Downloading KUTTL CRDs...\033[0m"
    just download-kuttl-crds
    @echo -e "\033[1;35m==> Importing KUTTL CRDs...\033[0m"
    just import-kuttl-crds