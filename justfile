# Build the project
build:
    uv run maturin develop

# Run Python tests
test:
    uv run pytest tests/ -v

# Run all checks
test-all: build test lint clippy fmt-check

# Lint Python code
lint:
    uv run ruff check python/ tests/

# Format Python code
format:
    uv run ruff format python/ tests/

# Format Rust code
fmt:
    cargo fmt

# Check Rust formatting
fmt-check:
    cargo fmt --check

# Run clippy
clippy:
    cargo clippy -- -D warnings

# Type check
typecheck:
    uv run mypy python/

# Clean build artifacts
clean:
    cargo clean
    rm -rf build/ dist/ *.egg-info
