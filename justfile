set ignore-comments := true

# Export PyO3 env vars so that maturin and cargo share dependency caches in the
# same target/ directory. Without these, maturin sets PYO3_ENVIRONMENT_SIGNATURE
# and PYO3_PYTHON when it invokes cargo, but plain `cargo test`/`cargo clippy`
# leave them unset. PyO3's build script watches these via rerun-if-env-changed,
# so any mismatch invalidates the cache and triggers a full PyO3 rebuild.
# See: https://github.com/PyO3/pyo3/issues/2724
# See: https://github.com/PyO3/pyo3/issues/5439
export PYO3_ENVIRONMENT_SIGNATURE := `uv run python -c "import struct, sys; print(f'cpython-{sys.version_info.major}.{sys.version_info.minor}-{struct.calcsize(\"P\") * 8}bit')"`
export PYO3_PYTHON := `uv run python -c "import pathlib, sys; print(pathlib.Path(sys.executable).parent / 'python')"`

pre-commit-args := ""
pytest-args := ""
mypy-args := ""
cargo-test-args := ""

[default]
[doc("List available recipes")]
list:
    @just --list

[doc("Initial repo setup after cloning")]
setup:
    uv run pre-commit install

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

# Docs

[doc("Build docs")]
[group("docs")]
docs-build: build
    uv run mkdocs build --strict

alias db := docs-build

[doc("Serve docs dev server")]
[group("docs")]
docs-serve: build
    uv run mkdocs serve --strict

alias ds := docs-serve

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

[doc("Run all checks (formatting, linting, type-checking, testing, docs, etc.)")]
check: fix test docs-build

alias c := check

[doc("Upgrade pre-commit hooks")]
pre-commit-upgrade:
    uv run pre-commit autoupdate

[doc("Upgrade all dependencies")]
[parallel]
upgrade: py-upgrade rs-upgrade pre-commit-upgrade

alias u := upgrade
