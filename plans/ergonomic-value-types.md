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
    grid_row=GridLine(start=GridPlacement.line(1), end=GridPlacement.span(2)),
)
```

Two problems:

1. **Verbosity**: `LengthPercentageAuto.length(10)` and `GridTrack.flex(1)` are painful to type. Users want `Length(10)` and `Fraction(1)`. The old helpers (`length()`, `percent()`, `auto()`) only returned `Dimension`, so they couldn't even be used for padding, margin, border, gap, or inset fields.
2. **No pattern matching**: Dimension-like values are opaque objects. Users can call `is_auto()` but can't destructure them with Python 3.10+ `match`/`case`. Similarly, `AvailableSpace.value()` returns `float | None`, defeating mypy narrowing after `is_definite()` guards.

## Waxy ↔ Taffy Type Reference

Complete mapping between waxy Python types and their underlying taffy 0.9.x Rust types. Types marked with *(removing)* are deleted by this plan; types marked with *(new)* are added. All others are unchanged.

`#[pyclass]` markers: **frozen** = immutable from Python; **unsendable** = wraps taffy's `CompactLength` (contains `*const ()`, not `Send`).

### Exceptions (`src/errors.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `TaffyException` | `TaffyError` | — | Base exception; maps from `TaffyError` variants |
| `ChildIndexOutOfBounds` | `TaffyError::ChildIndexOutOfBounds` | — | Subclass of `TaffyException` |
| `InvalidParentNode` | `TaffyError::InvalidParentNode` | — | Subclass of `TaffyException` |
| `InvalidChildNode` | `TaffyError::InvalidChildNode` | — | Subclass of `TaffyException` |
| `InvalidInputNode` | `TaffyError::InvalidInputNode` | — | Subclass of `TaffyException` |

### Geometry (`src/geometry.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `Size` | `Size<f32>` | frozen | `width`, `height`; also used for `Layout` fields |
| `Rect` | `Rect<f32>` | frozen | `left`, `right`, `top`, `bottom` |
| `Point` | `Point<f32>` | frozen | `x`, `y`; arithmetic ops supported |
| `Line` | `Line<f32>` | frozen | `start`, `end` — a 1D line segment |
| `KnownDimensions` | `Size<Option<f32>>` | frozen | Optional `width`/`height` for measure functions |
| `AvailableDimensions` | `Size<AvailableSpace>` | frozen, unsendable | Inputs/outputs change to new value types |

### Enums (`src/enums.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `Display` | `Display` | — | `Nil` maps to taffy's `None` (Python keyword conflict) |
| `Position` | `Position` | — | `Relative`, `Absolute` |
| `FlexDirection` | `FlexDirection` | — | `Row`, `Column`, `RowReverse`, `ColumnReverse` |
| `FlexWrap` | `FlexWrap` | — | `NoWrap`, `Wrap`, `WrapReverse` |
| `AlignItems` | `AlignItems` | — | Also serves as `AlignSelf`, `JustifySelf`, `JustifyItems` (type aliases in taffy) |
| `AlignContent` | `AlignContent` | — | Also serves as `JustifyContent` (type alias in taffy) |
| `Overflow` | `Overflow` | — | `Visible`, `Clip`, `Hidden`, `Scroll` |
| `GridAutoFlow` | `GridAutoFlow` | — | `Row`, `Column`, `RowDense`, `ColumnDense` |
| `BoxSizing` | `BoxSizing` | — | `BorderBox`, `ContentBox` |
| `TextAlign` | `TextAlign` | — | `Auto`, `LegacyLeft`, `LegacyRight`, `LegacyCenter` |

### Dimension & available-space types (`src/dimensions.rs` → `src/values.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `Dimension` *(removing)* | `Dimension` | frozen, unsendable | Opaque wrapper with static methods |
| `LengthPercentage` *(removing)* | `LengthPercentage` | frozen, unsendable | Opaque wrapper with static methods |
| `LengthPercentageAuto` *(removing)* | `LengthPercentageAuto` | frozen, unsendable | Opaque wrapper with static methods |
| `AvailableSpace` *(removing)* | `AvailableSpace` | unsendable | Opaque wrapper with static methods; in `src/enums.rs` |
| `Length` *(new)* | Variant of `Dimension` / `LengthPercentage` / etc. | frozen | `Length(value)` — shared across all dimension contexts |
| `Percent` *(new)* | Variant of `Dimension` / `LengthPercentage` / etc. | frozen | `Percent(value)` — shared across all dimension contexts |
| `Auto` *(new)* | Variant of `Dimension` / `LengthPercentageAuto` / `GridPlacement` | frozen | `Auto()` — shared across dimensions and grid placement |
| `MinContent` *(new)* | `AvailableSpace::MinContent` / `MinTrackSizingFunction::MinContent` | frozen | Also used in grid track sizing |
| `MaxContent` *(new)* | `AvailableSpace::MaxContent` / `MinTrackSizingFunction::MaxContent` | frozen | Also used in grid track sizing |
| `Definite` *(new)* | `AvailableSpace::Definite(f32)` | frozen | Available space only |

New types don't wrap `CompactLength`, so none need `unsendable`.

### Grid track types (`src/grid.rs` → `src/values.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `GridTrack` *(removing)* | `MinMax<MinTrackSizingFunction, MaxTrackSizingFunction>` | frozen, unsendable | Opaque wrapper with static methods |
| `GridTrackMin` *(removing)* | `MinTrackSizingFunction` | frozen, unsendable | Opaque wrapper with static methods |
| `GridTrackMax` *(removing)* | `MaxTrackSizingFunction` | frozen, unsendable | Opaque wrapper with static methods |
| `Fraction` *(new)* | `MaxTrackSizingFunction::Fraction(f32)` | frozen | CSS `fr` unit |
| `Minmax` *(new)* | `MinMax<MinTrackSizingFunction, MaxTrackSizingFunction>` | frozen | Explicit min/max pair; CSS `minmax()` |
| `FitContent` *(new)* | `MaxTrackSizingFunction::FitContent(LengthPercentage)` | frozen | CSS `fit-content()` |

Grid track getters recognize shorthand forms: `MinMax(length(v), length(v))` → `Length(v)`, `MinMax(auto, fr(v))` → `Fraction(v)`, etc.

### Grid placement types (`src/grid.rs` / `src/values.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `GridPlacement` *(removing)* | `GridPlacement` (enum: `Auto \| Line(GridLine) \| Span(u16)`) | frozen, unsendable | Opaque wrapper with static methods |
| `Line` *(new)* | `GridPlacement::Line(GridLine)` where `GridLine(i16)` | frozen | A 1-based grid line index; **naming conflict with geometry `Line`** — see note below |
| `Span` *(new)* | `GridPlacement::Span(u16)` | frozen | Span a number of tracks |
| `GridLine` | `Line<GridPlacement>` | frozen, unsendable | Start/end pair of placements; inputs/outputs change to new value types |

`Auto` (from shared types above) covers `GridPlacement::Auto`.

**Naming conflict**: The new `Line` (grid line index, from taffy's `GridLine(i16)`) collides with the existing geometry `Line` (from taffy's `Line<f32>`). Resolution TBD — see discussion in plan.

### Style (`src/style.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `Style` | `Style` | frozen, unsendable | All-kwargs constructor; `__or__` merges; inputs/outputs change to new value types |

### Layout (`src/layout.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `Layout` | `Layout` | frozen | Read-only computed layout; `order`, `location`, `size`, `content_size`, `scrollbar_size`, `border`, `padding`, `margin` |

### Node & tree (`src/node.rs`, `src/tree.rs`)

| Waxy type | Taffy type | Markers | Notes |
|---|---|---|---|
| `NodeId` | `NodeId` | frozen | Opaque node handle; `__eq__`, `__hash__` |
| `TaffyTree` | `TaffyTree<PyObject>` | unsendable | Mutable tree; generic over node context type in `.pyi` stubs |

### Helper functions (`src/helpers.rs` — all removing)

| Waxy function | Returned type | Notes |
|---|---|---|
| `zero()` *(removing)* | `LengthPercentage` | Use `Length(0)` instead |
| `auto()` *(removing)* | `Dimension` | Use `AUTO` or `Auto()` instead |
| `length()` *(removing)* | `Dimension` | Use `Length(v)` instead |
| `percent()` *(removing)* | `Dimension` | Use `Percent(v)` instead |
| `min_content()` *(removing)* | `AvailableSpace` | Use `MIN_CONTENT` or `MinContent()` instead |
| `max_content()` *(removing)* | `AvailableSpace` | Use `MAX_CONTENT` or `MaxContent()` instead |
| `fr()` *(removing)* | `GridTrack` | Use `Fraction(v)` instead |
| `minmax()` *(removing)* | `GridTrack` | Use `Minmax(min, max)` instead |

### Module-level constants (`src/values.rs` — all new)

| Waxy constant | Type | Notes |
|---|---|---|
| `AUTO` *(new)* | `Auto` | Singleton convenience; `AUTO` is `Auto()` |
| `MIN_CONTENT` *(new)* | `MinContent` | Singleton convenience |
| `MAX_CONTENT` *(new)* | `MaxContent` | Singleton convenience |

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
class Line:
    """A grid line index (1-based, negative indices count from the end)."""
    __match_args__ = ("index",)
    def __init__(self, index: int) -> None: ...
    @property
    def index(self) -> int: ...

class Span:
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
| `GridPlacement` | `Line \| Span \| Auto` | `GridLine.start`, `GridLine.end` |

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
match grid_line.start:
    case Line(n):
        print(f"line {n}")
    case Span(n):
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
        grid_row: GridLine | None = None,
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
enum GridPlacementInput { Line(Line), Span(Span), Auto(Auto) }
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

### GridLine Changes

`GridLine` stays as a class, but its `start`/`end` accept and return the new types:

```python
class GridLine:
    def __init__(
        self,
        start: Line | Span | Auto | None = None,  # None defaults to Auto
        end: Line | Span | Auto | None = None,
    ) -> None: ...
    @property
    def start(self) -> Line | Span | Auto: ...
    @property
    def end(self) -> Line | Span | Auto: ...
```

Before vs after:

```python
# Before
GridLine(start=GridPlacement.line(1), end=GridPlacement.span(3))

# After
GridLine(start=Line(1), end=Span(3))
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
    grid_row=GridLine(start=GridPlacement.line(1), end=GridPlacement.span(2)),
)

# After
Style(
    size_width=Length(10),
    padding_left=Length(10),
    margin_left=AUTO,
    grid_template_columns=[Length(200), Fraction(1), Fraction(2)],
    grid_template_rows=[AUTO, Minmax(Length(100), Fraction(1))],
    grid_row=GridLine(start=Line(1), end=Span(2)),
)
```

## Implementation Steps

### Step 1: Add new value types

In a new file `src/values.rs`, add all new types:

- **Shared**: `Length`, `Percent`, `Auto`, `MinContent`, `MaxContent` — frozen pyclasses with `__init__`, properties, `__repr__`, `__eq__`, `__hash__`, `__match_args__`
- **Available space**: `Definite` — frozen pyclass with `f32` field
- **Grid track**: `Fraction`, `FitContent`, `Minmax` — frozen pyclasses
- **Grid placement**: `Line` (frozen pyclass with `i16` field), `Span` (frozen pyclass with `u16` field)
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
- `GridPlacementInput` — `Line | Span | Auto`

### Step 3: Add taffy→value-type conversion helpers

Functions that inspect taffy's internal types and return the appropriate new Python type as `PyObject`:

- `dimension_to_py()` — for `taffy::Dimension` → `Length | Percent | Auto`
- `length_percentage_to_py()` — for `taffy::LengthPercentage` → `Length | Percent`
- `length_percentage_auto_to_py()` — for `taffy::LengthPercentageAuto` → `Length | Percent | Auto`
- `available_space_to_py()` — for `taffy::AvailableSpace` → `Definite | MinContent | MaxContent`
- `grid_track_to_py()` — for `TrackSizingFunction` → shorthand or `Minmax`
- `grid_placement_to_py()` — for `TaffyGridPlacement` → `Line | Span | Auto`

### Step 4: Update Style constructor and getters

- Change `set_field!` macro calls to use the new input enums
- Change getters to return new types via the conversion helpers
- Grid template fields accept `Vec<GridTrackInput>` and return converted lists
- Remove all imports of old types from `style.rs`

### Step 5: Update `GridLine`

- Constructor accepts `GridPlacementInput` for `start`/`end`
- Properties return `Line | Span | Auto` via `grid_placement_to_py()`
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
- Delete `GridTrack`, `GridTrackMin`, `GridTrackMax`, `GridPlacement` from `src/grid.rs` (keep `GridLine`)
- Remove all registrations from `lib.rs`
- Remove from `python/waxy/__init__.py` exports

### Step 8: Update Python exports and stubs

- `python/waxy/__init__.py` — add new types to imports and `__all__`, remove old types
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style/GridLine/AvailableDimensions signatures, remove old type stubs. Every class gets a class-level docstring matching the Rust doc comment. Every `__init__` parameter and property that isn't self-evident gets a docstring. Follow the existing stub conventions (see current `.pyi` for examples).
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
  - `GridLine` with `Line`, `Span`, `Auto` for start/end
  - `Minmax` and `FitContent` construction and destructuring
  - `AvailableDimensions` with new types
  - Measure function using pattern matching on `AvailableDimensions`
- Update existing tests that use old types (in `test_style.py`, `test_integration.py`, `test_measure.py`, etc.)

### Step 10: Update CLAUDE.md

- Architecture table: replace `dimensions.rs` and `helpers.rs` entries with `values.rs`, update the contents column
- Key design decisions: document that dimension-like values are now standalone frozen types (not enum-with-static-methods), list the new types, note that `CompactLength`/`unsendable` no longer applies to value types
- Remove mentions of deleted types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`, `GridTrack`, `GridTrackMin`, `GridTrackMax`, `GridPlacement`) and deleted helpers

### Step 11: Verify docstrings

Spot-check that every new public type has:
- A Rust doc comment that becomes `__doc__` in Python
- A matching docstring in the `.pyi` stub
- CSS concept cross-references where applicable (`Fraction` → `fr`, `Minmax` → `minmax()`, `FitContent` → `fit-content()`, `MinContent` → `min-content`, `MaxContent` → `max-content`)

### Step 12: Run `just check`
