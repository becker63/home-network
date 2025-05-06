default:
    @echo ""
    @just list

[working-directory: 'scripts']
list:
    @uv run invoke --list
    @just --list

# Run an invoke task
[working-directory: 'scripts']
invoke task-name args="":
    @uv run invoke {{task-name}} {{args}}
