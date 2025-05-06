default:
    @echo ""
    @just list

# Install all tools listed in .tool-versions
install-tools:
    asdf install

[working-directory: 'scripts']
list:
    @uv run invoke --list
    @just --list

# Run an invoke task
[working-directory: 'scripts']
invoke task-name args="":
    @uv run invoke {{task-name}} {{args}}
