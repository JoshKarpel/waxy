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

1. **Verbosity**: `LengthPercentageAuto.length(10)` and `GridTrack.flex(1)` are painful to type. Users want `Length(10)` and `Fr(1)`. The old helpers (`length()`, `percent()`, `auto()`) only returned `Dimension`, so they couldn't even be used for padding, margin, border, gap, or inset fields.
2. **No pattern matching**: Dimension-like values are opaque objects. Users can call `is_auto()` but can't destructure them with Python 3.10+ `match`/`case`. Similarly, `AvailableSpace.value()` returns `float | None`, defeating mypy narrowing after `is_definite()` guards.

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

#### Grid track only

```python
class Fr:
    """A fractional grid track unit."""
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
        max: Length | Percent | Auto | MinContent | MaxContent | Fr | FitContent,
    ) -> None: ...
    @property
    def min(self) -> Length | Percent | Auto | MinContent | MaxContent: ...
    @property
    def max(self) -> Length | Percent | Auto | MinContent | MaxContent | Fr | FitContent: ...

class FitContent:
    """A fit-content grid track sizing function."""
    __match_args__ = ("limit",)
    def __init__(self, limit: Length | Percent) -> None: ...
    @property
    def limit(self) -> Length | Percent: ...
```

#### Grid placement only

```python
class Span:
    """Span a number of grid tracks."""
    __match_args__ = ("count",)
    def __init__(self, count: int) -> None: ...
    @property
    def count(self) -> int: ...
```

Grid line indices are plain `int` — no wrapper class needed. `Auto` is reused for auto-placement.

#### Naming: `Percent` vs `Percentage`

Use `Percent` because:
- It's shorter
- CSS reads as "50 percent" not "50 percentage"

### How They Replace the Old Types

| Removed Type | Replacement Union | Used By |
|---|---|---|
| `Dimension` | `Length \| Percent \| Auto` | `size_*`, `min_size_*`, `max_size_*`, `flex_basis` |
| `LengthPercentage` | `Length \| Percent` | `padding_*`, `border_*`, `gap_*` |
| `LengthPercentageAuto` | `Length \| Percent \| Auto` | `margin_*`, `inset_*` |
| `AvailableSpace` | `Definite \| MinContent \| MaxContent` | `AvailableDimensions` |
| `GridTrack` | `Length \| Percent \| Auto \| MinContent \| MaxContent \| Fr \| Minmax \| FitContent` | `grid_template_*`, `grid_auto_*` |
| `GridTrackMin` | `Length \| Percent \| Auto \| MinContent \| MaxContent` | `Minmax.min` |
| `GridTrackMax` | `Length \| Percent \| Auto \| MinContent \| MaxContent \| Fr \| FitContent` | `Minmax.max` |
| `GridPlacement` | `int \| Span \| Auto` | `GridLine.start`, `GridLine.end` |

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
    case Fr(v):
        print(f"{v}fr")
    case Minmax(min_val, max_val):
        print(f"minmax({min_val}, {max_val})")
    case FitContent(Length(v)):
        print(f"fit-content({v}px)")

# Grid placements
match grid_line.start:
    case int(n):
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
        grid_template_columns: list[Length | Percent | Auto | MinContent | MaxContent | Fr | Minmax | FitContent] | None = None,
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
enum GridTrackInput { Length(Length), Percent(Percent), Auto(Auto), MinContent(MinContent), MaxContent(MaxContent), Fr(Fr), Minmax(Minmax), FitContent(FitContent) }

#[derive(FromPyObject)]
enum GridPlacementInput { Int(i16), Span(Span), Auto(Auto) }
```

#### Getters

Style getters return the new types. Grid track getters recognize common shorthand forms and return the simplified type:

- `minmax(length(v), length(v))` → `Length(v)`
- `minmax(percent(v), percent(v))` → `Percent(v)`
- `minmax(auto, auto)` → `Auto()`
- `minmax(min_content, min_content)` → `MinContent()`
- `minmax(max_content, max_content)` → `MaxContent()`
- `minmax(auto, fr(v))` → `Fr(v)`
- `minmax(auto, fit_content_px(v))` → `FitContent(Length(v))`
- `minmax(auto, fit_content_percent(v))` → `FitContent(Percent(v))`
- Everything else → `Minmax(min, max)`

This means what you put in is what you get back: `Fr(1)` round-trips as `Fr(1)`, not `Minmax(Auto(), Fr(1))`.

### GridLine Changes

`GridLine` stays as a class, but its `start`/`end` accept and return the new types:

```python
class GridLine:
    def __init__(
        self,
        start: int | Span | Auto | None = None,  # None defaults to Auto
        end: int | Span | Auto | None = None,
    ) -> None: ...
    @property
    def start(self) -> int | Span | Auto: ...
    @property
    def end(self) -> int | Span | Auto: ...
```

Before vs after:

```python
# Before
GridLine(start=GridPlacement.line(1), end=GridPlacement.span(3))

# After
GridLine(start=1, end=Span(3))
```

### Before / After Summary

```python
# Before
Style(
    size_width=Dimension.length(10),
    padding_left=LengthPercentage.length(10),
    margin_left=LengthPercentageAuto.auto(),
    grid_template_columns=[GridTrack.length(200), GridTrack.flex(1), GridTrack.flex(2)],
    grid_template_rows=[GridTrack.auto(), GridTrack.minmax(GridTrackMin.length(100), GridTrackMax.fr(1))],
    grid_row=GridLine(start=GridPlacement.line(1), end=GridPlacement.span(2)),
)

# After
Style(
    size_width=Length(10),
    padding_left=Length(10),
    margin_left=AUTO,
    grid_template_columns=[Length(200), Fr(1), Fr(2)],
    grid_template_rows=[AUTO, Minmax(Length(100), Fr(1))],
    grid_row=GridLine(start=1, end=Span(2)),
)
```

## Implementation Steps

### Step 1: Add new value types

In a new file `src/values.rs`, add all new types:

- **Shared**: `Length`, `Percent`, `Auto`, `MinContent`, `MaxContent` — frozen pyclasses with `__init__`, properties, `__repr__`, `__eq__`, `__hash__`, `__match_args__`
- **Available space**: `Definite` — frozen pyclass with `f32` field
- **Grid track**: `Fr`, `FitContent`, `Minmax` — frozen pyclasses
- **Grid placement**: `Span` — frozen pyclass with `u16` field
- **Constants**: `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` — registered via `m.add()`

`Minmax` and `FitContent` store their inner values as `PyObject` (the new value types), not taffy types. Conversion to taffy happens at the point of use (Style constructor, etc.).

Register in `values::register()`, wire into `lib.rs`.

### Step 2: Add `FromPyObject` input enums

In `src/values.rs`, define the input enums with `to_taffy()` methods:

- `DimensionInput` — `Length | Percent | Auto`
- `LengthPercentageInput` — `Length | Percent`
- `LengthPercentageAutoInput` — `Length | Percent | Auto`
- `AvailableSpaceInput` — `Definite | MinContent | MaxContent`
- `GridTrackInput` — `Length | Percent | Auto | MinContent | MaxContent | Fr | Minmax | FitContent`
- `GridTrackMinInput` — `Length | Percent | Auto | MinContent | MaxContent`
- `GridTrackMaxInput` — `Length | Percent | Auto | MinContent | MaxContent | Fr | FitContent`
- `GridPlacementInput` — `i16 | Span | Auto`

### Step 3: Add taffy→value-type conversion helpers

Functions that inspect taffy's internal types and return the appropriate new Python type as `PyObject`:

- `dimension_to_py()` — for `taffy::Dimension` → `Length | Percent | Auto`
- `length_percentage_to_py()` — for `taffy::LengthPercentage` → `Length | Percent`
- `length_percentage_auto_to_py()` — for `taffy::LengthPercentageAuto` → `Length | Percent | Auto`
- `available_space_to_py()` — for `taffy::AvailableSpace` → `Definite | MinContent | MaxContent`
- `grid_track_to_py()` — for `TrackSizingFunction` → shorthand or `Minmax`
- `grid_placement_to_py()` — for `TaffyGridPlacement` → `int | Span | Auto`

### Step 4: Update Style constructor and getters

- Change `set_field!` macro calls to use the new input enums
- Change getters to return new types via the conversion helpers
- Grid template fields accept `Vec<GridTrackInput>` and return converted lists
- Remove all imports of old types from `style.rs`

### Step 5: Update `GridLine`

- Constructor accepts `GridPlacementInput` for `start`/`end`
- Properties return `int | Span | Auto` via `grid_placement_to_py()`
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
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style/GridLine signatures, remove old type stubs

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
  - Grid track round-tripping (e.g., `Fr(1)` in → `Fr(1)` out)
  - `GridLine` with `int`, `Span`, `Auto` for start/end
  - `Minmax` and `FitContent` construction and destructuring
  - `AvailableDimensions` with new types
  - Measure function using pattern matching on `AvailableDimensions`
- Update existing tests that use old types (in `test_style.py`, `test_integration.py`, `test_measure.py`, etc.)

### Step 10: Update CLAUDE.md

Update the architecture table and key design decisions to reflect the new types.

### Step 11: Run `just check`
