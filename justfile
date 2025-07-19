@_default:
    just --list

@_success message:
    echo "\033[0;32m{{ message }}\033[0m"

@_start_command message:
    just _success "\n{{ message }} ..."

format: format_just format_python

@format_just:
    just _start_command "Formatting Justfile"
    just --fmt --unstable

@format_python:
    just _start_command "Formatting Python"
    uvx ruff format

@lint: lint_python

@lint_python:
    just _start_command "Linting Python"
    uvx ruff check

@pre_commit: format lint

version_bump version:
    #!/usr/bin/env bash
    uv version --bump {{ version }}
    VERSION=$(uv version --short)
    git add pyproject.toml uv.lock
    git commit -m "Version bump to v$VERSION"
    git tag -a "v$VERSION"
    just _success "Version bumped to v$VERSION."
