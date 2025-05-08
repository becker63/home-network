default:
    @echo ""
    @just list

# Start the dev shell with needed tools
install-tools:
    nix develop

[working-directory: 'scripts']
list:
    @uv run invoke --list
    @just --list

# Run an invoke task
[working-directory: 'scripts']
invoke task-name args="":
    @uv run invoke {{task-name}} {{args}}
