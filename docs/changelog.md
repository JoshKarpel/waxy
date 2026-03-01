# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased](https://github.com/JoshKarpel/waxy/compare/v0.3.0...HEAD)

### Added

- `Point` is now hashable, enabling use in sets and as dictionary keys.

### Fixed

- `Point`, `KnownSize`, and `AvailableSize` `__hash__` now correctly normalize
  `-0.0` to `0.0` so that equal objects always hash identically.

### Changed

- Clarified `Layout` coordinate system in API docs: `location` is relative to the parent's
  border box origin, `size` is the border box dimensions, and documented all `Layout` fields.

## [0.3.0](https://github.com/JoshKarpel/waxy/compare/v0.2.0...v0.3.0) - 2026-02-24

### Added

- [#22](https://github.com/JoshKarpel/waxy/pull/22) Custom measure functions via an optional `measure` kwarg on `compute_layout`,
  enabling proper sizing of leaf nodes based on their content.
- [#22](https://github.com/JoshKarpel/waxy/pull/22) Generic node context support: `new_leaf_with_context`, `set_node_context`,
  and `get_node_context` methods on `TaffyTree`.
- [#29](https://github.com/JoshKarpel/waxy/pull/29) Ergonomic value types (`Length`, `Percent`, `Auto`, `MinContent`, `MaxContent`,
  `Definite`, `Fraction`, `FitContent`, `Minmax`, `GridLine`, `GridSpan`) as
  standalone frozen pyclasses with union-based style fields, replacing the
  previous 1:1 taffy enum representations.
- [#33](https://github.com/JoshKarpel/waxy/pull/33) `Rect.points()`, `Rect.rows()`, and `Rect.columns()` methods for iterating
  over integer pixel locations within a rectangle.

### Changed

- [#30](https://github.com/JoshKarpel/waxy/pull/30) Slotmap panics from accessing removed nodes are now raised as
  `InvalidNodeId(TaffyException, KeyError)` instead of weird internal `pyo3` exceptions.

## [0.2.0](https://github.com/JoshKarpel/waxy/compare/v0.1.0...v0.2.0) - 2026-02-16

### Added

- [#19](https://github.com/JoshKarpel/waxy/pull/19) `Style` merging via `__or__` — `a | b` produces a new style where the
  right-hand side takes precedence.
- [#19](https://github.com/JoshKarpel/waxy/pull/19) Helper methods on geometry objects (`Size`, `Rect`, `Point`, `Line`).
- [#9](https://github.com/JoshKarpel/waxy/pull/9) Documentation site using mkdocs-material and mkdocstrings.

### Changed

- [#19](https://github.com/JoshKarpel/waxy/pull/19) All types except `TaffyTree` are now immutable (`#[pyclass(frozen)]`).

## [0.1.0](https://github.com/JoshKarpel/waxy/releases/tag/v0.1.0) - 2026-02-14

Initial release — proof-of-concept Python wrapper around taffy.

### Added

- `TaffyTree` core API for building and computing layouts.
- `Style` struct with all-kwargs constructor.
- `Layout` result struct.
- `NodeId` wrapper.
- Geometry types: `Size`, `Rect`, `Point`, `Line`.
- Layout enums: `Display`, `Position`, `FlexDirection`, `FlexWrap`,
  `AlignItems`, `AlignContent`, `GridAutoFlow`, `Overflow`, `BoxSizing`.
- CI with GitHub Actions, release workflow with maturin.
