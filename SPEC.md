# Waxy

## Goal

The goal of this project is to write a Python wrapper around the Rust `taffy` UI layout library,
for use in any Python application that needs to do CSS-style layout,
including terminal applications, web applications, and desktop applications.

## Taffy

For more information about the `taffy` library, visit these links:

- [Taffy Repository](https://github.com/DioxusLabs/taffy)
- [Taffy Documentation](https://docs.rs/taffy/latest/taffy/)

## API Design

The initial API will be a thin wrapper that closely mirrors taffy's Rust API:
a `TaffyTree` object, node handles, and style structs. This keeps the binding layer
straightforward and easy to maintain in sync with upstream taffy.

A higher-level, more declarative API may be added later as a pure-Python
layer on top of the bindings.

## Taffy Version

Pin to taffy **0.9.x**. Track patch releases but don't automatically upgrade major/minor.

## Scope

All layout modes supported by taffy are in scope: flexbox, CSS grid, block layout, and others.

## Python Version

Minimum supported Python version: **3.13+**

## Distribution

Wheels will be published to PyPI for Linux, macOS, and Windows,
built via maturin and GitHub Actions CI, using
[PyPI trusted publishers](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
for authentication (no API tokens needed).

## Project Structure

Use maturin's default project layout (`maturin init`).

## Error Handling

All exceptions inherit from a base `TaffyException` class.
Subclass as necessary for specific error conditions (e.g., invalid node handles, style validation).

## Tooling

For Python tooling, we will use:

- [`uv`](https://docs.astral.sh/uv/) for Python virtual environment and package management
- [`pytest`](https://docs.pytest.org/en/stable/) for testing
- [`mypy`](https://mypy.readthedocs.io/en/stable/) for type checking
- [`ruff`](https://docs.astral.sh/ruff/) for linting and formatting

For Rust tooling, we will use:

- [`cargo`](https://doc.rust-lang.org/cargo/) for building and testing the Rust code

To build the bindings between Python and Rust, we use the `pyo3`/`maturin` toolchain:

- [PyO3 Repository](https://github.com/PyO3/pyo3)
- [PyO3 User Guide](https://pyo3.rs/)
- [PyO3 API Reference](https://docs.rs/pyo3/latest/pyo3/)
- [Maturin Repository](https://github.com/PyO3/maturin)
- [Maturin User Guide](https://maturin.rs/)

We will use [`just`](https://just.systems/man/en/) as a task runner to automate common development tasks,
such as building the library, running tests, etc.
Whenever we find a useful, repeatable command, we will add it to the `justfile`
so that it can be easily run by anyone working on the project.

We will use `pre-commit` to set up pre-commit hooks for running linters, formatters, and other checks before committing code.
This will help maintain code quality and consistency across the project.
