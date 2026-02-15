The goal of this project is to write a Pythonic wrapper around the Rust `taffy` UI layout library,
for use in any Python application that needs to do CSS-style layout, 
including terminal applications, web applications, and desktop applications.

For more information about the `taffy` library, visit these links:

- [Taffy Repository](https://github.com/DioxusLabs/taffy)
- [Taffy Documentation](https://docs.rs/taffy/latest/taffy/)

For Python tooling, we will use:

- [`pytest`](https://docs.pytest.org/en/stable/) for testing
- [`mypy`](https://mypy.readthedocs.io/en/stable/) for type checking
- [`ruff`](https://docs.astral.sh/ruff/) for linting and formatting

For Rust tooling, we will use:
- `cargo` for building and testing the Rust code (as usual)

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
