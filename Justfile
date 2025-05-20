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

# 3. run unit tests on charts (must fill in asserts first)
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

# 0–3. Full rebuild (TODO, rethink the file synth hashes maybe? So argo doesnt reapply all the time, sure its idempotent but yknow)
build:
  just clean
  just compile
  just synth
  just generate


# Download CRDs for Crossplane, DigitalOcean, and AWS
download-crds:
    mkdir -p crds
    curl -L https://doc.crds.dev/raw/github.com/crossplane/crossplane@v1.19.1 \
        -o crds/crossplane-core.yaml
    curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/provider-digitalocean@v0.2.0 \
        -o crds/provider-digitalocean.yaml
    curl -L https://doc.crds.dev/raw/github.com/crossplane/provider-aws@v0.52.5 \
        -o crds/provider-aws.yaml

    curl -L https://doc.crds.dev/raw/github.com/crossplane-contrib/function-patch-and-transform@v0.7.0 \
          -o crds/function-patch-transform.yaml

# Import those CRDs into CDK8s with explicit names
importcrds:
    bunx cdk8s import crds/crossplane-core.yaml
    bunx cdk8s import crds/provider-digitalocean.yaml
    bunx cdk8s import crds/provider-aws.yaml
    bunx cdk8s import crds/function-patch-transform.yaml
