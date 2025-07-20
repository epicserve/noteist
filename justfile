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
    uvx ruff check --select I --fix
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
    # Update __version__ in src/noteist/__init__.py
    sed -i "s/^__version__ = .*/__version__ = \"$VERSION\"/" src/noteist/__init__.py
    git add pyproject.toml uv.lock src/noteist/__init__.py
    git commit -m "Version bump to v$VERSION"
    git tag -a "v$VERSION" -m ""
    just _success "Version bumped to v$VERSION."
