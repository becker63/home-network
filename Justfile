# KCL Project Automation Justfile

# ────────────────
# Generate Go-based KCL schemas
# ────────────────
[working-directory: "configurations/schemas/go"]
gen-go-schema:
    go run schema-gen.go

# ────────────────
# Full environment setup
# ────────────────
all:
    just gen-go-schema
    fetch_helm_values
    fetch_crds

# ────────────────
# Git commit shortcut
# ────────────────
git-commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"
    git push

# ────────────────
# Run tests with optional filter
# ────────────────
[no-exit-message]
test K_EXPRESSION="":
    @bash -c 'if [ "{{K_EXPRESSION}}" = "" ]; then pytest; else pytest -k "{{K_EXPRESSION}}"; fi'

# ────────────────
# Synth pipeline
# ────────────────
[working-directory: "scripts"]
check-kcl:
    pytest src/kcl_tasks/check

clean-synth:
    rm -rf synth_yaml/*

[working-directory: "scripts"]
check-synth:
    pytest src/kcl_tasks/automation/kcl_synth_yaml.py

synth: check-kcl clean-synth check-synth
