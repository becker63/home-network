# KCL Project Automation Justfile

# ────────────────
# Generate Go-based KCL schemas
# ────────────────
[working-directory: "kcl/schemas/go"]
gen-go-schema:
    go run schema-gen.go

# ────────────────
# Full environment setup
# ────────────────
all:
    fetch_kcl_mod
    just gen-go-schema
    fetch_helm_values
    fetch_crds

# ────────────────
# Git commit shortcut
# ────────────────
[working-directory: "."]
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
