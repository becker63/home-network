CROSSPLANE_VERSION := "v1.19.1"
PROVIDER_HELM_VERSION := "v0.15.0"
PATCH_FN_VERSION := "v0.7.0"
ARGOCD_VERSION := "v2.10.7"

download-crds:
    mkdir -p crds
    curl -L https://doc.crds.dev/raw/github.com/crossplane/crossplane@{{CROSSPLANE_VERSION}} \
        -o crds/crossplane-core.yaml
    curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/provider-helm@{{PROVIDER_HELM_VERSION}} \
        -o crds/provider-helm.yaml
    curl -L https://raw.githubusercontent.com/argoproj/argo-cd/{{ARGOCD_VERSION}}/manifests/crds/application-crd.yaml \
        -o crds/argocd-application.yaml
    curl -L https://raw.githubusercontent.com/argoproj/argo-cd/{{ARGOCD_VERSION}}/manifests/crds/appproject-crd.yaml \
        -o crds/argocd-appproject.yaml

import-crds:
    kcl import -m crd -s -f crds/*.yaml

init-kcl:
    just download-crds
    just import-crds