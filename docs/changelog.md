# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased](https://github.com/JoshKarpel/waxy/compare/v0.6.0...HEAD)

## [0.6.0](https://github.com/JoshKarpel/waxy/compare/v0.5.0...v0.6.0) - 2026-10-10

### Added

- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Support for Python 3.15, with release wheels built for it.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Style` exposes the layout features added in taffy 0.10 through 0.14:
  `direction` (`Direction.Ltr`/`Rtl`),
  `float` and `clear` (`Float`, `Clear`),
  `contain` (`Contain`),
  `flex_line_count`,
  and `item_is_table`/`item_is_replaced`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Display.FlowRoot` and `FlexWrap.Balance`/`BalanceReverse`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Safe alignment and self-relative alignment:
  `AlignItems.SelfStart`/`SelfEnd`, and `Safe*` members of `AlignItems` and `AlignContent`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `size_*` and `flex_basis` accept the CSS sizing keywords
  `MIN_CONTENT`, `MAX_CONTENT`, `FitContent(limit)`, `FIT_CONTENT` (`FitContentKeyword`),
  and `STRETCH` (`Stretch`); `flex_basis` also accepts `CONTENT` (`Content`).
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Grid `repeat()` via `Repeat(count, tracks, line_names)`,
  with `count` an `int`, `AUTO_FILL`, or `AUTO_FIT`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Named grid lines via `grid_template_row_names`/`grid_template_column_names`,
  placed with `NamedGridLine` and `NamedGridSpan`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Grid template areas via `grid_template_areas`,
  built with `GridTemplateArea`/`GridTemplateAreas`
  or parsed from CSS strings with `GridTemplateAreas.from_strings`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `TaffyTree.detailed_layout_info()` returns a `DetailedGridInfo` for grid containers:
  track positions, line names, item placements, and resolved `grid-template-*` strings,
  plus `resolve_absolute_grid_area()` for placing absolutely positioned children.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `InvalidFlexLineCount`, `InvalidRepeat`,
  `InvalidGridTemplateArea`, and `InvalidGridTemplateAreas`,
  raised for values that taffy would otherwise panic on during layout.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Layout.content_box_size()`, `content_box_x()`, `content_box_y()`,
  `scroll_width()`, and `scroll_height()`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `TaffyTree.remove_children_range()`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Style.fields_set`, the names of the explicitly set fields.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `TaffyTree.absolute_layouts(root)` returns every node in a subtree, in pre-order,
  with its absolute position and its `Layout`.
  With rounding enabled, each position is the sum of the unrounded locations rounded once,
  which matches taffy's rounded sizes.
  Summing rounded `location`s yourself can leave 1px gaps or overlaps between siblings,
  because taffy 0.14 rounds `location` relative to the parent but size in absolute coordinates
  ([taffy#834](https://github.com/DioxusLabs/taffy/issues/834),
  fixed upstream in [taffy#1189](https://github.com/DioxusLabs/taffy/pull/1189)
  but not yet released).
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `TaffyTree.format_tree(root)` returns an indented dump of a subtree
  (each node's id, location, size, and non-default style fields) as a string,
  unlike `print_tree`, which writes to stdout.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  A [performance guide](performance.md) for callers that lay out a tree every frame.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  The [API reference](api.md) documents every property, including those of the geometry and
  value types, and the module constants (`AUTO`, `STRETCH`, `AUTO_FILL`, ...).

### Changed

- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  Upgraded taffy from 0.9 to 0.14, which fixes many layout bugs across block, flexbox, and grid
  and so can change computed layouts.
  See [taffy's changelog](https://github.com/DioxusLabs/taffy/blob/main/CHANGELOG.md).
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Layout.content_size` is replaced by `Layout.scrollable_overflow_rect`,
  a `Rect` whose `right`/`bottom` are the old width/height.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `DimensionValue` includes the new sizing keywords,
  so `margin_*`, `inset_*`, `min_size_*`, and `max_size_*`,
  which don't accept them, are typed `LengthPercentageAutoValue` instead.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Style` equality and hashing take into account which fields were explicitly set,
  so two styles are equal only if they also merge identically.
  Styles can no longer be compared by layout alone:
  `Style() == Style(display=Display.Flex)` is `False`, though `Flex` is the default.
  `TaffyTree.style(node)` marks every field set,
  so it equals the style passed to `set_style` only if that style set every field.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Style(...)` raises `TypeError` for an unknown keyword argument instead of ignoring it.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  A value of the wrong type for a value union
  (in `Style`, `AvailableSize`, `Minmax`, `Repeat`, `GridPlacement`, ...)
  raises a one-line `TypeError` naming the accepted types,
  e.g. `expected Length | Percent | Auto, got int`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `repr(Style(...))` lists the explicitly set fields, as constructor syntax
  (`Style(flex_grow=1.0, border_top=Length(1))`).
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `TaffyTree.set_style` does nothing when the new style's values equal the node's current style,
  so the node keeps its cached layout.
  Use `mark_dirty` to force a relayout.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `compute_layout` calls the `measure` callback at most once per node
  for each distinct `(known_size, available_size)` input within one call,
  reusing the earlier result for repeats.
  This assumes the callback returns the same size for the same inputs within one layout.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Style` construction and hashing are faster,
  and release wheels are built with link-time optimization.

### Fixed

- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  After the `measure` callback raised, the next `compute_layout` reused the zero sizes
  from the failed call instead of measuring the affected leaves again.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `repr(Layout)` shows its location and size as `Point(...)` and `Size(...)`
  instead of Rust debug output.

### Removed

- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Rect` geometry methods, since taffy's `Rect` holds one value per side
  (like margin, padding and border) rather than a box:
  `width`, `height`, `size`, `contains`,
  `top_left`, `top_right`, `bottom_left`, `bottom_right`, `corners`,
  `top_edge`, `bottom_edge`, `left_edge`, `right_edge`,
  `points`, `rows`, `columns`, `intersection`, iteration, and `len()`.
- [#49](https://github.com/JoshKarpel/waxy/pull/49)
  `Line.length`, `Line.contains`, iteration, and `len()`.
  `Line` remains as a start/end pair, as in `DetailedGridTracksInfo.positions`.

## [0.5.0](https://github.com/JoshKarpel/waxy/compare/v0.4.0...v0.5.0) - 2026-04-03

### Added

- [#45](https://github.com/JoshKarpel/waxy/pull/45) `Rect.intersection(other)` returns the intersection rectangle (including edge-touching degenerate intersections), or `None` if the two rectangles do not intersect.

## [0.4.0](https://github.com/JoshKarpel/waxy/compare/v0.3.0...v0.4.0) - 2026-03-01

### Added

- [#36](https://github.com/JoshKarpel/waxy/pull/36) `Point` is now hashable, enabling use in sets and as dictionary keys.
- [#38](https://github.com/JoshKarpel/waxy/pull/38) `Style` now supports value equality via `==` and is hashable.
- [#39](https://github.com/JoshKarpel/waxy/pull/39) `Rect`, `Size`, `Line`, `GridPlacement`, and `Layout` are now hashable, enabling use in sets and as dictionary keys.
- [#39](https://github.com/JoshKarpel/waxy/pull/39) `GridPlacement` and `Layout` now support value equality via `==`.

### Changed

- [#35](https://github.com/JoshKarpel/waxy/pull/35) Clarified `Layout` coordinate system in API docs: `location` is relative to the parent's border box origin, `size` is the border box dimensions, and documented all `Layout` fields.

### Fixed

- [#36](https://github.com/JoshKarpel/waxy/pull/36) `Point`, `KnownSize`, and `AvailableSize` `__hash__` now correctly normalize `-0.0` to `0.0` so that equal objects always hash identically.

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
