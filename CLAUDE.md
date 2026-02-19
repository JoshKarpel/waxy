# Waxy

A Python wrapper around the Rust `taffy` UI layout library, built with PyO3/maturin.

## Key Files

- `plans/` — Design documents: `initial-concept.md` (project goals, tooling, design decisions), `measure-functions.md` (measure function design), `ergonomic-value-types.md` (value type refactor).

## Architecture

The Rust source (`src/`) exposes a flat PyO3 module `_waxy`, which Python (`python/waxy/__init__.py`) re-exports. Each Rust file maps to a domain:

| File | Contents |
|------|----------|
| `src/lib.rs` | PyO3 module definition, wires all submodules |
| `src/errors.rs` | `WaxyException`, `TaffyException` + 4 subclasses, `InvalidPercent` |
| `src/geometry.rs` | `Size`, `Rect`, `Point`, `Line`, `KnownSize`, `AvailableSize` |
| `src/values.rs` | `Length`, `Percent`, `Auto`, `MinContent`, `MaxContent`, `Definite`, `Fraction`, `FitContent`, `Minmax`, `GridLine`, `GridSpan`, `GridPlacement`; module constants `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` |
| `src/enums.rs` | All layout enums (`Display`, `Position`, `FlexDirection`, etc.) |
| `src/style.rs` | `Style` struct with all-kwargs constructor and getter/setter properties |
| `src/node.rs` | `NodeId` wrapper |
| `src/layout.rs` | `Layout` result struct (read-only) |
| `src/tree.rs` | `TaffyTree` — core API |

## Key Design Decisions

- **`#[pyclass(unsendable)]`** is required on all types that wrap taffy's `CompactLength` (which contains `*const ()`, not `Send`). This includes: `GridPlacement`, `Style`, `TaffyTree`. Value types in `src/values.rs` convert *to* taffy types but don't store them, so they don't need `unsendable`.
- **`#[pyclass(frozen)]`** is used on all types except `TaffyTree` (which is inherently mutable). All structs are immutable from Python — construct new instances instead of mutating.
- **Value types** (`Length`, `Percent`, `Auto`, `MinContent`, `MaxContent`, `Definite`, `Fraction`, `FitContent`, `Minmax`, `GridLine`, `GridSpan`) are standalone frozen pyclasses, not enum variants. They support `match`/`case` pattern matching via `__match_args__`. Module-level constants `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` are provided for the zero-argument types.
- **Exception hierarchy**: `WaxyException(Exception)` is the root. `TaffyException(WaxyException)` covers taffy errors with 4 subclasses. `InvalidPercent(WaxyException, ValueError)` is raised when `Percent` is constructed outside `[0.0, 1.0]`.
- **`Display.Nil`** maps to taffy's `Display::None`. We use `#[pyo3(name = "Nil")]` because `None` is a Python keyword.
- **`AlignSelf`/`JustifySelf`/`JustifyItems`** are type aliases for `AlignItems` in taffy. **`JustifyContent`** is an alias for `AlignContent`. We reuse the same Python enum types.
- **Grid template tracks** — `GridTemplateComponent<String>` repeat variants are silently skipped when converting from taffy. Only `Single(TrackSizingFunction)` is round-tripped.
- **Measure functions** are supported via an optional `measure` kwarg on `compute_layout`. The Rust closure auto-skips nodes without context (returns `Size::ZERO`) and short-circuits when both dimensions are known. The user's Python measure function receives `(known_size, available_size, context)` — taffy also passes `node_id` and `style` internally, but waxy doesn't forward them (the context identifies the node, and the tree is mutably borrowed so you can't call back into it). See `plans/measure-functions.md` for full design rationale.
- **`compute_layout`** takes an `available` kwarg (type `AvailableSize | None`), not `available_space`.
- **Node context** — `TaffyTree` uses `TaffyTree<PyObject>` internally. Nodes can have arbitrary Python objects attached via `new_leaf_with_context` / `set_node_context` / `get_node_context`. The `.pyi` stub uses `TaffyTree[T]` (PEP 695) for generic type safety.
- **Removed node access** causes a Rust panic (slotmap behavior), not a `TaffyError`.
- **`.pyi` method order** — Within each class: `__init__` first, then other dunder methods (`__repr__`, `__eq__`, `__iter__`, etc.), then properties, then regular methods.

## Commands

**Always run `just check` before committing.** It runs formatting, linting, pre-commit hooks, tests, docs, etc.

- `just check` (alias `c`) — the everything command: fix, test, typecheck, then pre-commit hooks
- `just fix` (alias `f`) — `git add --update` + `pre-commit run` (format, lint, and pre-commit hooks)
- `just test` (alias `t`) — py-test (mypy + pytest) + rs-test (cargo test) in parallel
- `just build` — `uv run maturin develop`
- `just lint` — py-lint (ruff check) + rs-lint (clippy --fix)
- `just format` — py-format (ruff format) + rs-format (cargo fmt)
- `just upgrade` (alias `u`) — upgrade Python, Rust, and pre-commit dependencies

All test/check commands accept override variables from the command line:

- `just pytest-args="-k test_style" test`
- `just mypy-args="--no-strict" py-test`
- `just cargo-test-args="-- --nocapture" rs-test`
- `just pre-commit-args="--all-files" fix`

## Dependencies

Add Python packages with `uv add <package>` (not by editing `pyproject.toml`) and Rust packages with `cargo add <package>` (not by editing `Cargo.toml`). This ensures lockfiles stay in sync.

## Adding a New Taffy Type or Field

1. Add the Rust wrapper in the appropriate `src/*.rs` file
2. Add `From` conversions in both directions (taffy ↔ wrapper)
3. Register the class/function in that file's `register()` function
4. Add the export to `python/waxy/__init__.py`
5. Add the type signature **and docstrings** to `python/waxy/__init__.pyi` (docstrings are required for members to appear in the rendered docs)
6. Add tests in `tests/`
7. Run `just check`

## Documentation (mkdocstrings)

Docstrings for the API reference come from **`python/waxy/__init__.pyi`**, not from Rust `///` doc comments. griffe (the backend for mkdocstrings-python) reads stub files for compiled PyO3 extensions; Rust `///` comments on `#[getter]` functions produce empty `__doc__` strings at runtime and are not useful for docs.

`show_if_no_docstring` defaults to `False` in mkdocstrings-python, so **any property or method without a docstring in the `.pyi` file will be silently omitted from the rendered docs**. Always add docstrings to `.pyi` entries when you want them to appear.

## Taffy Version

Pinned to taffy **0.9.x**. The taffy source can be inspected at:
`~/.cargo/registry/src/index.crates.io-*/taffy-0.9.*/`
