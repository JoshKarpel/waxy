pre-commit-args := ""
pytest-args := ""
mypy-args := ""
cargo-test-args := ""

[default]
[doc("List available recipes")]
list:
    @just --list

[doc("Build the extension module")]
build:
    uv run maturin develop

# Python

[doc("Type-check and test Python")]
[group("python")]
py-test: build
    uv run mypy {{ mypy-args }}
    uv run pytest {{ pytest-args }}

[doc("Lint and auto-fix Python code")]
[group("python")]
py-lint:
    uv run ruff check

[doc("Format Python code")]
[group("python")]
py-format:
    uv run ruff format

[doc("Clean Python build artifacts")]
[group("python")]
py-clean:
    rm -rf build/ dist/ *.egg-info

[doc("Upgrade Python dependencies")]
[group("python")]
py-upgrade:
    uv lock --upgrade

# Rust

[doc("Run Rust tests")]
[group("rust")]
rs-test:
    cargo test {{ cargo-test-args }}

[doc("Format Rust code")]
[group("rust")]
rs-format:
    cargo fmt

[doc("Run clippy with auto-fix")]
[group("rust")]
rs-lint:
    cargo clippy --fix --allow-dirty

[doc("Clean Rust build artifacts")]
[group("rust")]
rs-clean:
    cargo clean

[doc("Upgrade Rust dependencies")]
[group("rust")]
rs-upgrade:
    cargo update

# Combined

[doc("Run all tests")]
[parallel]
test: py-test rs-test

alias t := test

[doc("Format all code")]
[parallel]
format: py-format rs-format

[doc("Lint all code")]
[parallel]
lint: py-lint rs-lint

[doc("Clean all build artifacts")]
[parallel]
clean: py-clean rs-clean

_fix: format lint

fix:
    git add --update
    uv run pre-commit run {{ pre-commit-args }}

alias f := fix

[doc("Run all checks (formatting, linting, type-checking, testing, etc.)")]
check: fix test

alias c := check

[doc("Upgrade all dependencies")]
[parallel]
upgrade: py-upgrade rs-upgrade pre-commit-upgrade

alias u := upgrade

[doc("Upgrade pre-commit hooks")]
pre-commit-upgrade:
    uv run pre-commit autoupdate
