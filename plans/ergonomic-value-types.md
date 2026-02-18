# Plan: Ergonomic Value Types (Issue #27)

## Problem

The current API for dimension and grid values is verbose and inflexible:

```python
# Verbose — each container type has its own static constructors
Style(
    size_width=Dimension.length(10),
    padding_left=LengthPercentage.length(10),
    margin_left=LengthPercentageAuto.length(10),
    grid_template_columns=[GridTrack.length(200), GridTrack.flex(1), GridTrack.flex(2)],
    grid_row=GridPlacement(start=GridPlacement.line(1), end=GridPlacement.span(2)),
)
```

Two problems:

1. **Verbosity**: `LengthPercentageAuto.length(10)` and `GridTrack.flex(1)` are painful to type. Users want `Length(10)` and `Fraction(1)`. The old helpers (`length()`, `percent()`, `auto()`) only returned `Dimension`, so they couldn't even be used for padding, margin, border, gap, or inset fields.
2. **No pattern matching**: Dimension-like values are opaque objects. Users can call `is_auto()` but can't destructure them with Python 3.10+ `match`/`case`. Similarly, `AvailableSpace.value()` returns `float | None`, defeating mypy narrowing after `is_definite()` guards.

## Waxy ↔ Taffy Type Reference

Complete mapping between waxy Python types and their underlying taffy 0.9.x Rust types, as they will exist after this plan is implemented.

### Exceptions (`src/errors.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `TaffyException` | `TaffyError` | Base exception for all taffy errors; each `TaffyError` variant maps to a subclass below |
| `ChildIndexOutOfBounds` | `TaffyError::ChildIndexOutOfBounds` | Raised when accessing a child by index beyond `child_count` |
| `InvalidParentNode` | `TaffyError::InvalidParentNode` | Raised when a parent `NodeId` doesn't exist in the tree |
| `InvalidChildNode` | `TaffyError::InvalidChildNode` | Raised when a child `NodeId` doesn't exist in the tree |
| `InvalidInputNode` | `TaffyError::InvalidInputNode` | Raised when an input `NodeId` doesn't exist in the tree |
| `InvalidPercent` | — | Raised when `Percent(value)` is called with `value` outside 0.0–1.0; inherits from both `TaffyException` and `ValueError` |

### Geometry (`src/geometry.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Size` | `Size<f32>` | `width` and `height` floats; also the return type for `Layout.size`, `Layout.content_size`, `Layout.scrollbar_size`; supports `area` property |
| `Rect` | `Rect<f32>` | `left`, `right`, `top`, `bottom` floats; derived `width`, `height`, `size` properties; `contains(point)` hit-testing; corner/edge iteration; also the return type for `Layout.border`, `Layout.padding`, `Layout.margin` |
| `Point` | `Point<f32>` | `x`, `y` floats; arithmetic ops (`+`, `-`, `*`, `/`, unary `-`); also the return type for `Layout.location` |
| `Line` | `Line<f32>` | `start`, `end` floats — a 1D line segment; `length` and `contains(value)` methods |
| `KnownSize` | `Size<Option<f32>>` | `width` and `height` as `float \| None`; passed to measure functions to indicate already-known dimensions |
| `AvailableSize` | `Size<AvailableSpace>` | `width` and `height` as `Definite \| MinContent \| MaxContent`; passed to measure functions to indicate available layout space |

### Enums (`src/enums.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Display` | `Display` | `Block`, `Flex`, `Grid`, `Nil`; `Nil` maps to taffy's `None` because `None` is a Python keyword |
| `Position` | `Position` | `Relative`, `Absolute` |
| `FlexDirection` | `FlexDirection` | `Row`, `Column`, `RowReverse`, `ColumnReverse` |
| `FlexWrap` | `FlexWrap` | `NoWrap`, `Wrap`, `WrapReverse` |
| `AlignItems` | `AlignItems` | `Start`, `End`, `FlexStart`, `FlexEnd`, `Center`, `Baseline`, `Stretch`; waxy reuses this type for `AlignSelf`, `JustifySelf`, and `JustifyItems` (which are type aliases in taffy) |
| `AlignContent` | `AlignContent` | `Start`, `End`, `FlexStart`, `FlexEnd`, `Center`, `Stretch`, `SpaceBetween`, `SpaceEvenly`, `SpaceAround`; waxy reuses this type for `JustifyContent` (a type alias in taffy) |
| `Overflow` | `Overflow` | `Visible`, `Clip`, `Hidden`, `Scroll` |
| `GridAutoFlow` | `GridAutoFlow` | `Row`, `Column`, `RowDense`, `ColumnDense` |
| `BoxSizing` | `BoxSizing` | `BorderBox`, `ContentBox` |
| `TextAlign` | `TextAlign` | `Auto`, `LegacyLeft`, `LegacyRight`, `LegacyCenter`; these are **not** standard `text-align` — they implement the block-level child alignment behavior of HTML's `<center>` and `<div align="...">`, corresponding to browser-internal `-webkit-center` etc. The "Legacy" prefix distinguishes from standard text alignment (which is a text-rendering concern, not layout) |

### Value types (`src/values.rs`)

These replace the old `Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`, `GridTrack`, `GridTrackMin`, `GridTrackMax`, `GridPlacement` types and all helper functions. None wrap `CompactLength`, so none need `unsendable`.

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Length` | `Dimension::Length(f32)`, `LengthPercentage::Length(f32)`, etc. | A length in pixels; `Length(value)` with a `value` property; shared across all dimension, padding/border/gap, margin/inset, and grid track contexts |
| `Percent` | `Dimension::Percent(f32)`, `LengthPercentage::Percent(f32)`, etc. | A percentage (0.0–1.0); `Percent(value)` with a `value` property; shared across all the same contexts as `Length`; constructor validates `0.0 <= value <= 1.0` and raises `InvalidPercent` if not |
| `Auto` | `Dimension::Auto`, `LengthPercentageAuto::Auto`, `GridPlacement::Auto` | Automatic sizing / auto-placement; `Auto()` with no fields; shared across dimension, margin/inset, grid track, and grid placement contexts |
| `MinContent` | `AvailableSpace::MinContent`, `MinTrackSizingFunction::MinContent` | CSS `min-content` intrinsic sizing; `MinContent()` with no fields; used in available space and grid track min/max sizing |
| `MaxContent` | `AvailableSpace::MaxContent`, `MinTrackSizingFunction::MaxContent` | CSS `max-content` intrinsic sizing; `MaxContent()` with no fields; used in available space and grid track min/max sizing |
| `Definite` | `AvailableSpace::Definite(f32)` | A definite available space in pixels; `Definite(value)` with a `value` property; used only in `AvailableSize` (measure function input) |
| `Fraction` | `MaxTrackSizingFunction::Fraction(f32)` | CSS `fr` unit — a fractional share of remaining grid space; `Fraction(value)` with a `value` property; used only in grid track sizing |
| `Minmax` | `MinMax<MinTrackSizingFunction, MaxTrackSizingFunction>` | CSS `minmax()` — explicit min/max track sizing pair; `Minmax(min, max)` where `min` is `Length \| Percent \| Auto \| MinContent \| MaxContent` and `max` adds `Fraction \| FitContent`; used only in grid track sizing |
| `FitContent` | `MaxTrackSizingFunction::FitContent(LengthPercentage)` | CSS `fit-content()` — grow up to a limit then clamp; `FitContent(limit)` where `limit` is `Length \| Percent`; used only in grid track sizing |
| `GridLine` | `GridPlacement::Line(GridLine)` where `GridLine(i16)` | A 1-based grid line index (negative counts from end); `GridLine(index)` with an `index` property; used only in grid placement |
| `GridSpan` | `GridPlacement::Span(u16)` | Span a number of grid tracks; `GridSpan(count)` with a `count` property; used only in grid placement |

Grid track getters recognize shorthand forms: `MinMax(length(v), length(v))` → `Length(v)`, `MinMax(auto, fr(v))` → `Fraction(v)`, etc. This means round-tripping preserves the concise form.

### Grid (`src/grid.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `GridPlacement` | `Line<GridPlacement>` | A start/end pair of grid placements; `GridPlacement(start, end)` where each is `GridLine \| GridSpan \| Auto` (defaults to `Auto`); wraps taffy's generic `Line<T>` specialized to grid placements |

### Style (`src/style.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Style` | `Style` | All layout properties as keyword-only constructor args; frozen (construct new instances to change); `__or__` merges two styles (right side wins for fields it sets); all dimension/grid fields accept and return the new value types |

### Layout (`src/layout.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Layout` | `Layout` | Read-only computed layout result; properties: `order` (int), `location` (Point), `size` (Size), `content_size` (Size), `scrollbar_size` (Size), `border` (Rect), `padding` (Rect), `margin` (Rect); derived: `content_box_width()`, `content_box_height()` |

### Node & tree (`src/node.rs`, `src/tree.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `NodeId` | `NodeId` | Opaque handle to a node in the tree; hashable and equality-comparable; accessing a removed node panics (slotmap behavior) |
| `TaffyTree` | `TaffyTree<PyObject>` | The mutable layout tree; nodes hold an optional Python object as context (for identifying nodes in measure functions); `.pyi` stubs use `TaffyTree[T]` for generic type safety over the context type |

### Module-level constants (`src/values.rs`)

| Waxy constant | Type | Notes |
|---|---|---|
| `AUTO` | `Auto` | Module-level singleton; `AUTO is Auto()` for convenience — avoids constructing `Auto()` repeatedly |
| `MIN_CONTENT` | `MinContent` | Module-level singleton for `MinContent()` |
| `MAX_CONTENT` | `MaxContent` | Module-level singleton for `MaxContent()` |

## Documentation Links

Taffy docs live on docs.rs; CSS concepts are documented on MDN. Link to both in Rust doc comments (which PyO3 surfaces as Python `__doc__`) and `.pyi` docstrings.

### Value types

| Waxy type | Taffy docs | MDN |
|---|---|---|
| `Length` | [Dimension::Length](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html) | [&lt;length&gt;](https://developer.mozilla.org/en-US/docs/Web/CSS/length) |
| `Percent` | [Dimension::Percent](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html) | [&lt;percentage&gt;](https://developer.mozilla.org/en-US/docs/Web/CSS/percentage) |
| `Auto` | [Dimension::Auto](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html) | — (per-property) |
| `MinContent` | [MinTrackSizingFunction::MinContent](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html) | [min-content](https://developer.mozilla.org/en-US/docs/Web/CSS/min-content) |
| `MaxContent` | [MinTrackSizingFunction::MaxContent](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html) | [max-content](https://developer.mozilla.org/en-US/docs/Web/CSS/max-content) |
| `Definite` | [AvailableSpace::Definite](https://docs.rs/taffy/0.9.2/taffy/style/enum.AvailableSpace.html) | — |
| `Fraction` | [MaxTrackSizingFunction::Fraction](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html) | [&lt;flex&gt;](https://developer.mozilla.org/en-US/docs/Web/CSS/flex_value) |
| `Minmax` | [TrackSizingFunction](https://docs.rs/taffy/0.9.2/taffy/style/enum.TrackSizingFunction.html) | [minmax()](https://developer.mozilla.org/en-US/docs/Web/CSS/minmax) |
| `FitContent` | [MaxTrackSizingFunction::FitContent](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html) | [fit-content()](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content_function) |
| `GridLine` | [GridPlacement::Line](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html) | [Line-based placement](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_line-based_placement) |
| `GridSpan` | [GridPlacement::Span](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html) | [grid-column-start (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column-start) |

### Enums

| Waxy type | Taffy docs | MDN |
|---|---|---|
| `Display` | [Display](https://docs.rs/taffy/0.9.2/taffy/style/enum.Display.html) | [display](https://developer.mozilla.org/en-US/docs/Web/CSS/display) |
| `Position` | [Position](https://docs.rs/taffy/0.9.2/taffy/style/enum.Position.html) | [position](https://developer.mozilla.org/en-US/docs/Web/CSS/position) |
| `FlexDirection` | [FlexDirection](https://docs.rs/taffy/0.9.2/taffy/style/enum.FlexDirection.html) | [flex-direction](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-direction) |
| `FlexWrap` | [FlexWrap](https://docs.rs/taffy/0.9.2/taffy/style/enum.FlexWrap.html) | [flex-wrap](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-wrap) |
| `AlignItems` | [AlignItems](https://docs.rs/taffy/0.9.2/taffy/style/enum.AlignItems.html) | [align-items](https://developer.mozilla.org/en-US/docs/Web/CSS/align-items) |
| `AlignContent` | [AlignContent](https://docs.rs/taffy/0.9.2/taffy/style/enum.AlignContent.html) | [align-content](https://developer.mozilla.org/en-US/docs/Web/CSS/align-content) |
| `Overflow` | [Overflow](https://docs.rs/taffy/0.9.2/taffy/style/enum.Overflow.html) | [overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow) |
| `GridAutoFlow` | [GridAutoFlow](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridAutoFlow.html) | [grid-auto-flow](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-flow) |
| `BoxSizing` | [BoxSizing](https://docs.rs/taffy/0.9.2/taffy/style/enum.BoxSizing.html) | [box-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing) |
| `TextAlign` | [TextAlign](https://docs.rs/taffy/0.9.2/taffy/style/enum.TextAlign.html) | [text-align](https://developer.mozilla.org/en-US/docs/Web/CSS/text-align) |

### Style fields

| Style field | Taffy docs | MDN |
|---|---|---|
| `display` | [Style::display](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.display) | [display](https://developer.mozilla.org/en-US/docs/Web/CSS/display) |
| `position` | [Style::position](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.position) | [position](https://developer.mozilla.org/en-US/docs/Web/CSS/position) |
| `overflow_x`, `overflow_y` | [Style::overflow](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.overflow) | [overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow) |
| `box_sizing` | [Style::box_sizing](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.box_sizing) | [box-sizing](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing) |
| `flex_direction` | [Style::flex_direction](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.flex_direction) | [flex-direction](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-direction) |
| `flex_wrap` | [Style::flex_wrap](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.flex_wrap) | [flex-wrap](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-wrap) |
| `flex_grow` | [Style::flex_grow](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.flex_grow) | [flex-grow](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-grow) |
| `flex_shrink` | [Style::flex_shrink](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.flex_shrink) | [flex-shrink](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-shrink) |
| `flex_basis` | [Style::flex_basis](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.flex_basis) | [flex-basis](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis) |
| `align_items` | [Style::align_items](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.align_items) | [align-items](https://developer.mozilla.org/en-US/docs/Web/CSS/align-items) |
| `align_self` | [Style::align_self](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.align_self) | [align-self](https://developer.mozilla.org/en-US/docs/Web/CSS/align-self) |
| `align_content` | [Style::align_content](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.align_content) | [align-content](https://developer.mozilla.org/en-US/docs/Web/CSS/align-content) |
| `justify_items` | [Style::justify_items](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.justify_items) | [justify-items](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-items) |
| `justify_self` | [Style::justify_self](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.justify_self) | [justify-self](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-self) |
| `justify_content` | [Style::justify_content](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.justify_content) | [justify-content](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-content) |
| `size_width`, `size_height` | [Style::size](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.size) | [width](https://developer.mozilla.org/en-US/docs/Web/CSS/width), [height](https://developer.mozilla.org/en-US/docs/Web/CSS/height) |
| `min_size_width`, `min_size_height` | [Style::min_size](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.min_size) | [min-width](https://developer.mozilla.org/en-US/docs/Web/CSS/min-width), [min-height](https://developer.mozilla.org/en-US/docs/Web/CSS/min-height) |
| `max_size_width`, `max_size_height` | [Style::max_size](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.max_size) | [max-width](https://developer.mozilla.org/en-US/docs/Web/CSS/max-width), [max-height](https://developer.mozilla.org/en-US/docs/Web/CSS/max-height) |
| `aspect_ratio` | [Style::aspect_ratio](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.aspect_ratio) | [aspect-ratio](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio) |
| `margin_*` | [Style::margin](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.margin) | [margin](https://developer.mozilla.org/en-US/docs/Web/CSS/margin) |
| `padding_*` | [Style::padding](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.padding) | [padding](https://developer.mozilla.org/en-US/docs/Web/CSS/padding) |
| `border_*` | [Style::border](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.border) | [border-width](https://developer.mozilla.org/en-US/docs/Web/CSS/border-width) |
| `gap_row`, `gap_column` | [Style::gap](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.gap) | [gap](https://developer.mozilla.org/en-US/docs/Web/CSS/gap) |
| `inset_*` | [Style::inset](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.inset) | [inset](https://developer.mozilla.org/en-US/docs/Web/CSS/inset) |
| `grid_template_rows` | [Style::grid_template_rows](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_template_rows) | [grid-template-rows](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-rows) |
| `grid_template_columns` | [Style::grid_template_columns](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_template_columns) | [grid-template-columns](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-columns) |
| `grid_auto_rows` | [Style::grid_auto_rows](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_auto_rows) | [grid-auto-rows](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-rows) |
| `grid_auto_columns` | [Style::grid_auto_columns](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_auto_columns) | [grid-auto-columns](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-columns) |
| `grid_auto_flow` | [Style::grid_auto_flow](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_auto_flow) | [grid-auto-flow](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-flow) |
| `grid_row` | [Style::grid_row](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_row) | [grid-row](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row) |
| `grid_column` | [Style::grid_column](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.grid_column) | [grid-column](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column) |
| `text_align` | [Style::text_align](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html#structfield.text_align) | [text-align](https://developer.mozilla.org/en-US/docs/Web/CSS/text-align) |

### Other types

| Waxy type | Taffy docs |
|---|---|
| `Style` | [Style](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html) |
| `Layout` | [Layout](https://docs.rs/taffy/0.9.2/taffy/tree/struct.Layout.html) |
| `NodeId` | [NodeId](https://docs.rs/taffy/0.9.2/taffy/tree/struct.NodeId.html) |
| `TaffyTree` | [TaffyTree](https://docs.rs/taffy/0.9.2/taffy/struct.TaffyTree.html) |
| `Size` | [Size](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Size.html) |
| `Rect` | [Rect](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Rect.html) |
| `Point` | [Point](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Point.html) |
| `Line` | [Line](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Line.html) |
| `GridPlacement` | [Line&lt;GridPlacement&gt;](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Line.html) |

These links should be included in Rust doc comments (`/// ...`) and `.pyi` docstrings for each type and Style field. For example:

```rust
/// A percentage value (0.0 to 1.0).
///
/// See: [taffy `Dimension::Percent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html),
/// [MDN `<percentage>`](https://developer.mozilla.org/en-US/docs/Web/CSS/percentage)
```

## Design: Standalone Value Types

Replace the "enum with static methods" pattern with standalone Python classes — one per variant. This is the "poor man's Rust enum" approach: model each variant as its own type and use `Union` on the Python side.

The old container types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`, `GridTrack`, `GridTrackMin`, `GridTrackMax`, `GridPlacement`) are all removed entirely. No backward compatibility — waxy is pre-1.0 and a clean break is better than legacy baggage.

All old helper functions (`length()`, `percent()`, `auto()`, `zero()`, `min_content()`, `max_content()`, `fr()`, `minmax()`) are also deleted — the class constructors are equally concise.

### New Types

All types are `#[pyclass(frozen)]`. Value-carrying types get `__match_args__`, `__eq__`, `__hash__`, `__repr__`. None of these wrap `CompactLength`, so none need `unsendable`.

#### Shared across dimensions, available space, and grid tracks

```python
class Length:
    """A length value in pixels."""
    __match_args__ = ("value",)
    def __init__(self, value: float) -> None: ...
    @property
    def value(self) -> float: ...

class Percent:
    """A percentage value (0.0 to 1.0).

    Raises InvalidPercent (a subclass of both TaffyException and ValueError)
    if value is outside the range [0.0, 1.0].
    """
    __match_args__ = ("value",)
    def __init__(self, value: float) -> None: ...
    @property
    def value(self) -> float: ...

class Auto:
    """Automatic sizing."""
    def __init__(self) -> None: ...

AUTO: Auto  # Module-level constant

class MinContent:
    """Min-content sizing."""
    def __init__(self) -> None: ...

MIN_CONTENT: MinContent  # Module-level constant

class MaxContent:
    """Max-content sizing."""
    def __init__(self) -> None: ...

MAX_CONTENT: MaxContent  # Module-level constant
```

#### Available space only

```python
class Definite:
    """A definite available space in pixels."""
    __match_args__ = ("value",)
    def __init__(self, value: float) -> None: ...
    @property
    def value(self) -> float: ...
```

#### Grid track sizing only

A "grid track" is CSS terminology for a single row or column in a grid layout. These types define how a track should be sized.

```python
class Fraction:
    """A fractional unit of remaining grid space (CSS `fr` unit).

    After fixed lengths and percentages are allocated, remaining space
    is divided among fractional tracks proportionally. E.g., Fraction(1)
    and Fraction(2) in the same grid get 1/3 and 2/3 of remaining space.
    """
    __match_args__ = ("value",)
    def __init__(self, value: float) -> None: ...
    @property
    def value(self) -> float: ...

class Minmax:
    """A minmax grid track sizing function."""
    __match_args__ = ("min", "max")
    def __init__(
        self,
        min: Length | Percent | Auto | MinContent | MaxContent,
        max: Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent,
    ) -> None: ...
    @property
    def min(self) -> Length | Percent | Auto | MinContent | MaxContent: ...
    @property
    def max(self) -> Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent: ...

class FitContent:
    """A fit-content grid track sizing function."""
    __match_args__ = ("limit",)
    def __init__(self, limit: Length | Percent) -> None: ...
    @property
    def limit(self) -> Length | Percent: ...
```

#### Grid placement only

```python
class GridLine:
    """A grid line index (1-based, negative indices count from the end)."""
    __match_args__ = ("index",)
    def __init__(self, index: int) -> None: ...
    @property
    def index(self) -> int: ...

class GridSpan:
    """Span a number of grid tracks."""
    __match_args__ = ("count",)
    def __init__(self, count: int) -> None: ...
    @property
    def count(self) -> int: ...
```

`Auto` is reused for auto-placement.

#### Naming

**`Percent` vs `Percentage`**: Use `Percent` — it's shorter, and CSS reads as "50 percent" not "50 percentage".

**`Fraction` vs `Fr`**: Use `Fraction` — spell it out. `fr` is a CSS abbreviation that's opaque if you don't already know CSS grid. The docstring can mention the CSS `fr` unit for people coming from CSS.

### How They Replace the Old Types

| Removed Type | Replacement Union | Used By |
|---|---|---|
| `Dimension` | `Length \| Percent \| Auto` | `size_*`, `min_size_*`, `max_size_*`, `flex_basis` |
| `LengthPercentage` | `Length \| Percent` | `padding_*`, `border_*`, `gap_*` |
| `LengthPercentageAuto` | `Length \| Percent \| Auto` | `margin_*`, `inset_*` |
| `AvailableSpace` | `Definite \| MinContent \| MaxContent` | `AvailableSize` |
| `GridTrack` | `Length \| Percent \| Auto \| MinContent \| MaxContent \| Fraction \| Minmax \| FitContent` | `grid_template_*`, `grid_auto_*` |
| `GridTrackMin` | `Length \| Percent \| Auto \| MinContent \| MaxContent` | `Minmax.min` |
| `GridTrackMax` | `Length \| Percent \| Auto \| MinContent \| MaxContent \| Fraction \| FitContent` | `Minmax.max` |
| `GridPlacement` (old) | `GridLine \| GridSpan \| Auto` | `GridPlacement.start`, `GridPlacement.end` |

The key insight: `Length`, `Percent`, `Auto`, `MinContent`, `MaxContent` are shared across many contexts. A single small set of types covers the entire API.

### Pattern Matching

```python
# Dimension fields
match style.size_width:
    case Length(v):
        print(f"{v}px")
    case Percent(v):
        print(f"{v * 100}%")
    case Auto():
        print("auto")

# Available space in measure functions
match avail_w:
    case Definite(v):
        inline_size = v  # float — no Optional, no type: ignore
    case MinContent() | MaxContent():
        inline_size = len(context["text"]) * CHAR_WIDTH

# Grid tracks
match track:
    case Fraction(v):
        print(f"{v}fr")
    case Minmax(min_val, max_val):
        print(f"minmax({min_val}, {max_val})")
    case FitContent(Length(v)):
        print(f"fit-content({v}px)")

# Grid placements
match placement.start:
    case GridLine(n):
        print(f"line {n}")
    case GridSpan(n):
        print(f"span {n}")
    case Auto():
        print("auto")
```

### Style Changes

#### Constructor

```python
class Style:
    def __init__(
        self,
        *,
        size_width: Length | Percent | Auto | None = None,
        padding_left: Length | Percent | None = None,
        margin_left: Length | Percent | Auto | None = None,
        grid_template_columns: list[Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent] | None = None,
        grid_row: GridPlacement | None = None,
        ...
    ) -> None: ...
```

On the Rust side, implemented with `#[derive(FromPyObject)]` input enums:

```rust
#[derive(FromPyObject)]
enum DimensionInput { Length(Length), Percent(Percent), Auto(Auto) }

#[derive(FromPyObject)]
enum LengthPercentageInput { Length(Length), Percent(Percent) }

#[derive(FromPyObject)]
enum LengthPercentageAutoInput { Length(Length), Percent(Percent), Auto(Auto) }

#[derive(FromPyObject)]
enum AvailableSpaceInput { Definite(Definite), MinContent(MinContent), MaxContent(MaxContent) }

#[derive(FromPyObject)]
enum GridTrackInput { Length(Length), Percent(Percent), Auto(Auto), MinContent(MinContent), MaxContent(MaxContent), Fraction(Fraction), Minmax(Minmax), FitContent(FitContent) }

#[derive(FromPyObject)]
enum GridPlacementInput { GridLine(GridLine), GridSpan(GridSpan), Auto(Auto) }
```

#### Getters

Style getters return the new types. Grid track getters recognize common shorthand forms and return the simplified type:

- `minmax(length(v), length(v))` → `Length(v)`
- `minmax(percent(v), percent(v))` → `Percent(v)`
- `minmax(auto, auto)` → `Auto()`
- `minmax(min_content, min_content)` → `MinContent()`
- `minmax(max_content, max_content)` → `MaxContent()`
- `minmax(auto, fr(v))` → `Fraction(v)`
- `minmax(auto, fit_content_px(v))` → `FitContent(Length(v))`
- `minmax(auto, fit_content_percent(v))` → `FitContent(Percent(v))`
- Everything else → `Minmax(min, max)`

This means what you put in is what you get back: `Fraction(1)` round-trips as `Fraction(1)`, not `Minmax(Auto(), Fraction(1))`.

### GridPlacement Changes

`GridPlacement` (renamed from `GridLine`) stays as a class, but its `start`/`end` accept and return the new types:

```python
class GridPlacement:
    def __init__(
        self,
        start: GridLine | GridSpan | Auto | None = None,  # None defaults to Auto
        end: GridLine | GridSpan | Auto | None = None,
    ) -> None: ...
    @property
    def start(self) -> GridLine | GridSpan | Auto: ...
    @property
    def end(self) -> GridLine | GridSpan | Auto: ...
```

Before vs after:

```python
# Before
GridPlacement(start=GridPlacement.line(1), end=GridPlacement.span(3))

# After
GridPlacement(start=GridLine(1), end=GridSpan(3))
```

### Before / After Summary

```python
# Before
Style(
    size_width=Dimension.length(10),
    padding_left=LengthPercentage.length(10),
    margin_left=LengthPercentageAuto.auto(),
    grid_template_columns=[GridTrack.length(200), GridTrack.flex(1), GridTrack.flex(2)],  # "flex" is taffy's name for CSS fr
    grid_template_rows=[GridTrack.auto(), GridTrack.minmax(GridTrackMin.length(100), GridTrackMax.fr(1))],
    grid_row=GridPlacement(start=GridPlacement.line(1), end=GridPlacement.span(2)),
)

# After
Style(
    size_width=Length(10),
    padding_left=Length(10),
    margin_left=AUTO,
    grid_template_columns=[Length(200), Fraction(1), Fraction(2)],
    grid_template_rows=[AUTO, Minmax(Length(100), Fraction(1))],
    grid_row=GridPlacement(start=GridLine(1), end=GridSpan(2)),
)
```

## Implementation Steps

### Step 1: Add new value types

In a new file `src/values.rs`, add all new types:

- **Shared**: `Length`, `Percent`, `Auto`, `MinContent`, `MaxContent` — frozen pyclasses with `__init__`, properties, `__repr__`, `__eq__`, `__hash__`, `__match_args__`
- **Available space**: `Definite` — frozen pyclass with `f32` field
- **Grid track**: `Fraction`, `FitContent`, `Minmax` — frozen pyclasses
- **Grid placement**: `GridLine` (frozen pyclass with `i16` field), `GridSpan` (frozen pyclass with `u16` field)
- **Constants**: `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` — registered via `m.add()`

Every type gets a Rust doc comment (`/// ...`) which PyO3 surfaces as Python `__doc__`. Use the docstrings from the "New Types" section above — they should explain what the type represents in plain language, not just repeat the type name. For types that map to CSS concepts (`Fraction`, `Minmax`, `FitContent`, `MinContent`, `MaxContent`), mention the CSS equivalent so users coming from CSS can orient themselves. Include links to taffy docs and MDN where applicable — see the "Documentation Links" section above for the full URL reference.

`Percent.__init__` validates `0.0 <= value <= 1.0` and raises `InvalidPercent` if not. Register `InvalidPercent` in `src/errors.rs` as a subclass of both `TaffyException` and `ValueError` (use `create_exception!` with `TaffyException` as the base, then set `__bases__` to include `ValueError` during module init).

`Minmax` and `FitContent` store their inner values as `PyObject` (the new value types), not taffy types. Conversion to taffy happens at the point of use (Style constructor, etc.).

Register in `values::register()`, wire into `lib.rs`.

### Step 2: Add `FromPyObject` input enums

In `src/values.rs`, define the input enums with `to_taffy()` methods:

- `DimensionInput` — `Length | Percent | Auto`
- `LengthPercentageInput` — `Length | Percent`
- `LengthPercentageAutoInput` — `Length | Percent | Auto`
- `AvailableSpaceInput` — `Definite | MinContent | MaxContent`
- `GridTrackInput` — `Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent`
- `GridTrackMinInput` — `Length | Percent | Auto | MinContent | MaxContent`
- `GridTrackMaxInput` — `Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent`
- `GridPlacementInput` — `GridLine | GridSpan | Auto`

### Step 3: Add taffy→value-type conversion helpers

Functions that inspect taffy's internal types and return the appropriate new Python type as `PyObject`:

- `dimension_to_py()` — for `taffy::Dimension` → `Length | Percent | Auto`
- `length_percentage_to_py()` — for `taffy::LengthPercentage` → `Length | Percent`
- `length_percentage_auto_to_py()` — for `taffy::LengthPercentageAuto` → `Length | Percent | Auto`
- `available_space_to_py()` — for `taffy::AvailableSpace` → `Definite | MinContent | MaxContent`
- `grid_track_to_py()` — for `TrackSizingFunction` → shorthand or `Minmax`
- `grid_placement_to_py()` — for `TaffyGridPlacement` → `GridLine | GridSpan | Auto`

### Step 4: Update Style constructor and getters

- Change `set_field!` macro calls to use the new input enums
- Change getters to return new types via the conversion helpers
- Grid template fields accept `Vec<GridTrackInput>` and return converted lists
- Remove all imports of old types from `style.rs`

### Step 5: Update `GridPlacement` (renamed from `GridLine`)

- Rename `GridLine` → `GridPlacement` in `src/grid.rs`
- Constructor accepts `GridPlacementInput` for `start`/`end`
- Properties return `GridLine | GridSpan | Auto` via `grid_placement_to_py()`
- Internal storage stays as `TaffyGridPlacement`

### Step 6: Update `AvailableSize`

In `src/geometry.rs`:

- Constructor accepts `AvailableSpaceInput`
- Properties return `Definite | MinContent | MaxContent`
- `__iter__` yields new types

### Step 7: Delete old types and helpers

- Delete `src/dimensions.rs` entirely
- Delete `src/helpers.rs` entirely
- Delete `AvailableSpace` from `src/enums.rs`
- Delete `GridTrack`, `GridTrackMin`, `GridTrackMax`, old `GridPlacement` from `src/grid.rs` (keep the renamed `GridPlacement`)
- Remove all registrations from `lib.rs`
- Remove from `python/waxy/__init__.py` exports

### Step 8: Update Python exports and stubs

- `python/waxy/__init__.py` — add new types to imports and `__all__`, remove old types
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style/GridPlacement/AvailableSize signatures, remove old type stubs. Every class gets a class-level docstring matching the Rust doc comment, including links to taffy docs and MDN (see "Documentation Links" section). Every `__init__` parameter and property that isn't self-evident gets a docstring. Every Style field docstring should link to its MDN page. Follow the existing stub conventions (see current `.pyi` for examples).
  - Add type aliases for the unions that appear repeatedly (e.g., `DimensionValue = Length | Percent | Auto`) to keep the Style signature readable — or spell them out inline if the aliases would obscure more than they help. Use judgment.

### Step 9: Update tests

- Delete `test_dimensions.py` (tests old types)
- Add new tests:
  - Construction and properties for each new type
  - `__repr__`, `__eq__`, `__hash__` for each
  - Pattern matching with `match`/`case` for all type families
  - `__match_args__` for positional destructuring
  - `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` constants
  - Style construction with new types (all field categories including grid)
  - Style getters return correct new types
  - Grid track round-tripping (e.g., `Fraction(1)` in → `Fraction(1)` out)
  - `GridPlacement` with `GridLine`, `GridSpan`, `Auto` for start/end
  - `Minmax` and `FitContent` construction and destructuring
  - `AvailableSize` with new types
  - Measure function using pattern matching on `AvailableSize`
- Update existing tests that use old types (in `test_style.py`, `test_integration.py`, `test_measure.py`, etc.)

### Step 10: Update CLAUDE.md

- Architecture table: replace `dimensions.rs` and `helpers.rs` entries with `values.rs`, update the contents column
- Key design decisions: document that dimension-like values are now standalone frozen types (not enum-with-static-methods), list the new types, note that `CompactLength`/`unsendable` no longer applies to value types
- Remove mentions of deleted types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`, `GridTrack`, `GridTrackMin`, `GridTrackMax`, old `GridPlacement`, old `GridLine`) and deleted helpers

### Step 11: Verify docstrings

Spot-check that every new public type has:
- A Rust doc comment that becomes `__doc__` in Python
- A matching docstring in the `.pyi` stub
- CSS concept cross-references where applicable (`Fraction` → `fr`, `Minmax` → `minmax()`, `FitContent` → `fit-content()`, `MinContent` → `min-content`, `MaxContent` → `max-content`)

### Step 12: Run `just check`
