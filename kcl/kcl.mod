[package]
name = "infra"
edition = "v0.11.1"
version = "0.0.1"

[dependencies]
argo-application-field-validation = "0.1.2"
argo-cd = "0.2.1"
cert-manager = "0.3.0"
crossplane = "1.17.3"
crossplane-provider-gcp = "0.22.2"
external-secrets = "0.1.4"
fluxcd = "0.1.2"
fluxcd-helm-controller = "v1.0.3"
fluxcd-kustomize-controller = "v1.3.2"
fluxcd-source-controller = "v1.3.2"
sealed-secrets = "v0.27.2"
traefik = "0.2.1"
