# Waxy

A Python wrapper around the Rust `taffy` UI layout library, built with PyO3/maturin.

## Key Files

- `plans/` — Design documents: `initial-concept.md` (project goals, tooling, design decisions), `measure-functions.md` (measure function design), `ergonomic-value-types.md` (value type refactor).
- `benchmarks/` — Timing suite and build-vs-build comparison for hot-path changes; its `README.md` covers the workflow (release builds, comparing builds rather than runs, profiling).

## Architecture

The Rust source (`src/`) exposes a flat PyO3 module `_waxy`, which Python (`python/waxy/__init__.py`) re-exports. Each Rust file maps to a domain:

| File | Contents |
|------|----------|
| `src/lib.rs` | PyO3 module definition, wires all submodules |
| `src/errors.rs` | `WaxyException`, `TaffyException` and its subclasses, and the `Invalid*` validation exceptions; panic-to-exception helpers |
| `src/geometry.rs` | `Size`, `Rect`, `Point`, `Line`, `KnownSize`, `AvailableSize` |
| `src/values.rs` | Value types (lengths, sizing keywords, grid tracks, `Repeat`, grid placements, template areas) with their `*Input` extractors and taffy-to-Python converters; module constants (`AUTO`, `STRETCH`, `AUTO_FILL`, ...) |
| `src/enums.rs` | All layout enums (`Display`, `AlignItems`, `Direction`, `Contain`, etc.) |
| `src/style.rs` | `Style` struct with all-kwargs constructor and getter/setter properties |
| `src/node.rs` | `NodeId` wrapper |
| `src/layout.rs` | `Layout` result (read-only, wraps `taffy::Layout`) and the `DetailedGridInfo` family |
| `src/tree.rs` | `TaffyTree` — core API |

## Key Design Decisions

- **No `#[pyclass(unsendable)]`**: pyo3 refuses to drop an `unsendable` object on any thread but its creator's, and a garbage collection can run on any thread, so every pyclass is `Send + Sync`. taffy's `CompactLength` holds a `*const ()`, which makes any taffy type containing it neither; `Style` and `TaffyTree` store their taffy values in `NoCalc` (`src/values.rs`), whose `unsafe impl`s rest on waxy never constructing `calc()` values. Value types in `src/values.rs` convert *to* taffy types but don't store them (`FitContent`, `Minmax`, and `Repeat` hold their parts as validated Python objects instead), so they need no wrapper.
- **`#[pyclass(frozen)]`** is used on all types except `TaffyTree` (which is inherently mutable). All structs are immutable from Python — construct new instances instead of mutating.
- **Value types** are standalone frozen pyclasses, not enum variants. They support `match`/`case` pattern matching via `__match_args__`. Each zero-argument type (`Auto`, `Stretch`, `AutoFill`, ...) has a module-level constant (`AUTO`, `STRETCH`, `AUTO_FILL`, ...). Where taffy accepts a value in some fields but not others (e.g. `Content` only in `flex_basis`, `Stretch` not in grid tracks), waxy uses separate `*Input` extractors and type aliases so the invalid combination fails at construction. Declare `*Input` extractors with the `input_enum!` macro in `src/values.rs`, not `#[derive(FromPyObject)]`: its cast-based extraction doesn't build an error per missed variant, and its `TypeError` names the accepted types.
- **Exception hierarchy**: `WaxyException(Exception)` is the root. `TaffyException(WaxyException)` covers taffy errors. `InvalidNodeId` is `TaffyException + KeyError` (raised when accessing a removed node). Validation exceptions (`Invalid*` other than `InvalidNodeId`) are `WaxyException + ValueError` via multi-inheritance, achieved by setting `__bases__` in `register()` in `src/errors.rs`. Validate wherever taffy would otherwise panic during layout (e.g. `Repeat` line name counts).
- **`Style` set fields**: `Style` records which fields were explicitly set in a bitmask, which `|` uses to merge, so `__eq__` and `__hash__` include it. Every `Style` is built through `Style::from_parts`, which creates the cached hash and debug-asserts that unset fields hold `taffy::Style::DEFAULT` values. The `FIELDS` table in `src/style.rs` lists every field name; its doc comment lists everything else a new field needs.
- **`Display.Nil`** maps to taffy's `Display::None`. We use `#[pyo3(name = "Nil")]` because `None` is a Python keyword.
- **`AlignSelf`/`JustifySelf`/`JustifyItems`** are type aliases for `AlignItems` in taffy. **`JustifyContent`** is an alias for `AlignContent`. We reuse the same Python enum types.
- **Alignment**: taffy models alignment as a `(keyword, safety)` struct. waxy flattens it into enum members (`AlignItems.SafeCenter`, ...) mirroring taffy's `SAFE_*` constants; the combinations taffy has no constant for (`safe baseline`, `safe stretch`, safe distributed alignment) are `unreachable!()` when converting back.
- **Grid line names**: `grid_template_*_names` are positional with `grid_template_*`: entry `i` names the line before template entry `i` (a `Repeat` counts as one entry), mirroring taffy's representation.
- **Measure functions** are supported via an optional `measure` kwarg on `compute_layout`. The Rust closure wraps the Python call in `taffy::compute_leaf_layout`, which applies the leaf's own padding, border, and min/max sizes around the measured content size; it skips nodes without context (content size `Size::ZERO`), short-circuits when both dimensions are known, and answers repeated `(node, known, available)` inputs from a memo that lives for one `compute_layout` call. The user's Python measure function receives `(known_size, available_size, context)` — taffy also passes `node_id` and `style` internally, but waxy doesn't forward them (the context identifies the node, and the tree is mutably borrowed so you can't call back into it). See `plans/measure-functions.md` for full design rationale.
- **`compute_layout`** takes an `available` kwarg (type `AvailableSize | None`), not `available_space`.
- **Node context** — `TaffyTree` uses `TaffyTree<PyObject>` internally. Nodes can have arbitrary Python objects attached via `new_leaf_with_context` / `set_node_context` / `get_node_context`. The `.pyi` stub uses `TaffyTree[T]` (PEP 695) for generic type safety.
- **Removed node access** raises `InvalidNodeId` (a `TaffyException` and `KeyError` subclass). This is implemented via `catch_unwind` around taffy calls, since taffy panics on invalid slotmap keys. The panic message is checked for slotmap signatures; non-slotmap panics become `TaffyException` instead to avoid misattribution. In `compute_layout` with a measure function, `py_err` lives outside the `catch_unwind` boundary (as a `RefCell`) so Python exceptions from the callback are preserved and take priority over panics.
- **No pyo3 reference pool** — `.cargo/config.toml` sets `--cfg pyo3_disable_reference_pool`, which removes a global mutex lock from every call into waxy. Never drop a `Py<T>` while detached from the interpreter (inside a `py.detach` closure, say): without the pool, that aborts the process. CI's `setup-rust-toolchain` sets `RUSTFLAGS`, which replaces the config's `rustflags`, so `ci.yml` repeats the flag; keep the two in sync.
- **Hashing helpers** — Use these `pub(crate)` functions when implementing `__hash__`:
  - `hash_f32()` in `src/geometry.rs` — for plain `f32` fields; normalizes `-0.0` to `+0.0` before `to_bits()`, required because `==` treats them as equal.
  - `hash_taffy_compact_length()` in `src/values.rs` — for a `CompactLength`; call `.into_raw()` first when the field is typed as `Dimension`, `LengthPercentage`, or `LengthPercentageAuto`.
  - `hash_taffy_track_sizing_function()` in `src/values.rs` — for a `TrackSizingFunction`.
  - `hash_taffy_template_component()` in `src/values.rs` — for a `GridTemplateComponent<String>`.
  - `hash_taffy_template_area()` in `src/values.rs` — for a `GridTemplateArea<String>`.
  - `hash_taffy_grid_placement()` in `src/values.rs` — for a `TaffyGridPlacement`.
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
- `just bench` — release build + `benchmarks/suite.py`; `just bench-build` only builds

All test/check commands accept override variables from the command line:

- `just pytest-args="-k test_style" test`
- `just mypy-args="--no-strict" py-test`
- `just cargo-test-args="-- --nocapture" rs-test`
- `just bench-args="-k compute --compare /tmp/before.json" bench`
- `just pre-commit-args="--all-files" fix`

## Dependencies

Add Python packages with `uv add <package>` (not by editing `pyproject.toml`) and Rust packages with `cargo add <package>` (not by editing `Cargo.toml`). This ensures lockfiles stay in sync.

## Adding a New Taffy Type or Field

1. Add the Rust wrapper in the appropriate `src/*.rs` file
2. Add `From` conversions in both directions (taffy ↔ wrapper)
3. Register the class/function in that file's `register()` function
4. Add the export to `python/waxy/__init__.py`
5. Add the type signature **and docstrings** to `python/waxy/__init__.pyi` (docstrings are required for members to appear in the rendered docs)
6. Add the entry to `docs/api.md` under the appropriate section
7. Add tests in `tests/`
8. Run `just check`

## Documentation (mkdocstrings)

Docstrings for the API reference come from **`python/waxy/__init__.pyi`**, not from Rust `///` doc comments. griffe (the backend for mkdocstrings-python) reads stub files for compiled PyO3 extensions; Rust `///` comments on `#[getter]` functions produce empty `__doc__` strings at runtime and are not useful for docs.

`show_if_no_docstring` defaults to `False` in mkdocstrings-python, so **any property or method without a docstring in the `.pyi` file will be silently omitted from the rendered docs**. Always add docstrings to `.pyi` entries when you want them to appear.

**Type aliases** (`DimensionValue`, `GridTrackValue`, etc.) are defined directly in `python/waxy/__init__.py` using PEP 695 `type` syntax. They are also mirrored in the `.pyi` stub for type checkers. griffe reads pure-Python names from the source file, so the docstrings on these aliases live in `__init__.py` itself, not the stub.

## Changelog

`docs/changelog.md` follows [Keep a Changelog](https://keepachangelog.com/) format. Add user-facing changes to the `[Unreleased]` section under the appropriate category (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`). Skip non-user-facing changes like CI tweaks and dependency bumps. List the PR link first on each item (e.g., `- [#123](https://github.com/JoshKarpel/waxy/pull/123) Description of change.`).

## Taffy Version

Pinned to taffy **0.14.x**. The taffy source can be inspected at:
`~/.cargo/registry/src/index.crates.io-*/taffy-0.14.*/`
