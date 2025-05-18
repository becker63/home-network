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

# 0–3. Full build & test cycle
all:
  just compile
  just synth
  just generate
  just test
