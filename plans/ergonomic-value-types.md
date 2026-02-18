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

### Geometry (`src/geometry.rs`)

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Size` | `Size<f32>` | `width` and `height` floats; also the return type for `Layout.size`, `Layout.content_size`, `Layout.scrollbar_size`; supports `area` property |
| `Rect` | `Rect<f32>` | `left`, `right`, `top`, `bottom` floats; derived `width`, `height`, `size` properties; `contains(point)` hit-testing; corner/edge iteration; also the return type for `Layout.border`, `Layout.padding`, `Layout.margin` |
| `Point` | `Point<f32>` | `x`, `y` floats; arithmetic ops (`+`, `-`, `*`, `/`, unary `-`); also the return type for `Layout.location` |
| `Line` | `Line<f32>` | `start`, `end` floats — a 1D line segment; `length` and `contains(value)` methods |
| `KnownDimensions` | `Size<Option<f32>>` | `width` and `height` as `float \| None`; passed to measure functions to indicate already-known dimensions |
| `AvailableDimensions` | `Size<AvailableSpace>` | `width` and `height` as `Definite \| MinContent \| MaxContent`; passed to measure functions to indicate available layout space |

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
| `TextAlign` | `TextAlign` | `Auto`, `LegacyLeft`, `LegacyRight`, `LegacyCenter` |

### Value types (`src/values.rs`)

These replace the old `Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`, `GridTrack`, `GridTrackMin`, `GridTrackMax`, `GridPlacement` types and all helper functions. None wrap `CompactLength`, so none need `unsendable`.

| Waxy type | Taffy type | Notes |
|---|---|---|
| `Length` | `Dimension::Length(f32)`, `LengthPercentage::Length(f32)`, etc. | A length in pixels; `Length(value)` with a `value` property; shared across all dimension, padding/border/gap, margin/inset, and grid track contexts |
| `Percent` | `Dimension::Percent(f32)`, `LengthPercentage::Percent(f32)`, etc. | A percentage (0.0–1.0); `Percent(value)` with a `value` property; shared across all the same contexts as `Length` |
| `Auto` | `Dimension::Auto`, `LengthPercentageAuto::Auto`, `GridPlacement::Auto` | Automatic sizing / auto-placement; `Auto()` with no fields; shared across dimension, margin/inset, grid track, and grid placement contexts |
| `MinContent` | `AvailableSpace::MinContent`, `MinTrackSizingFunction::MinContent` | CSS `min-content` intrinsic sizing; `MinContent()` with no fields; used in available space and grid track min/max sizing |
| `MaxContent` | `AvailableSpace::MaxContent`, `MinTrackSizingFunction::MaxContent` | CSS `max-content` intrinsic sizing; `MaxContent()` with no fields; used in available space and grid track min/max sizing |
| `Definite` | `AvailableSpace::Definite(f32)` | A definite available space in pixels; `Definite(value)` with a `value` property; used only in `AvailableDimensions` (measure function input) |
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
    """A percentage value (0.0 to 1.0)."""
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
| `AvailableSpace` | `Definite \| MinContent \| MaxContent` | `AvailableDimensions` |
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

Every type gets a Rust doc comment (`/// ...`) which PyO3 surfaces as Python `__doc__`. Use the docstrings from the "New Types" section above — they should explain what the type represents in plain language, not just repeat the type name. For types that map to CSS concepts (`Fraction`, `Minmax`, `FitContent`, `MinContent`, `MaxContent`), mention the CSS equivalent so users coming from CSS can orient themselves.

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

### Step 6: Update `AvailableDimensions`

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
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style/GridPlacement/AvailableDimensions signatures, remove old type stubs. Every class gets a class-level docstring matching the Rust doc comment. Every `__init__` parameter and property that isn't self-evident gets a docstring. Follow the existing stub conventions (see current `.pyi` for examples).
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
  - `AvailableDimensions` with new types
  - Measure function using pattern matching on `AvailableDimensions`
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
