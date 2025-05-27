[working-directory: "charts"]
import-crds:
    kcl mod add sealed-secrets:v0.27.2
    kcl mod add argo-cd:0.2.1
    kcl mod add cert-manager:0.3.0
    kcl mod add crossplane:1.17.3

[working-directory: "charts/schemas/frp_schema"]
gen-frp-schema:
    go run gen-schema.go

init-kcl:
    just import-crds
    just gen-frp-schema
