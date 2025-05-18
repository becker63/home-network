# _Hidden
_default: _help

_help:
  @just --list

_synth_yaml_validate:
  kubeconform synth_yaml/

# Run tests
test: _synth_yaml_validate

# Import Kubernetes definitions
import_cdk8s:
  cdk8s import

# Compile and synth
build: compile synth

# Generate Kubernetes YAML
synth:
  bunx cdk8s synth

# Compile ts
compile:
  bunx tsc --build
