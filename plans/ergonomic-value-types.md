# Plan: Ergonomic Value Types (Issue #27)

## Problem

The current API for dimension values is verbose and inflexible:

```python
# Verbose — each container type has its own static constructors
Style(
    size_width=Dimension.length(10),
    padding_left=LengthPercentage.length(10),
    margin_left=LengthPercentageAuto.length(10),
)

# Helpers exist, but only return Dimension
length(10)   # → Dimension — works for size_width but NOT for padding_left
percent(0.5) # → Dimension — same problem
auto()       # → Dimension
```

Two problems:

1. **Verbosity**: `LengthPercentageAuto.length(10)` is painful to type. Users want `Length(10)`. The old helpers (`length()`, `percent()`, `auto()`) only returned `Dimension`, so they couldn't even be used for padding, margin, border, gap, or inset fields.
2. **No pattern matching**: Dimension-like values are opaque objects. Users can call `is_auto()` but can't destructure them with Python 3.10+ `match`/`case`. Similarly, `AvailableSpace.value()` returns `float | None`, defeating mypy narrowing after `is_definite()` guards.

## Design: Standalone Value Types

Replace the "enum with static methods" pattern with standalone Python classes — one per variant. This is the "poor man's Rust enum" approach: model each variant as its own type and use `Union` on the Python side.

The old container types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`) are removed entirely. No backward compatibility — waxy is pre-1.0 and a clean break is better than legacy baggage.

### New Dimension Types

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
    """An automatic dimension."""
    def __init__(self) -> None: ...

AUTO: Auto  # Module-level constant for convenience
```

These are plain frozen pyclasses that store an `f32` (or nothing for `Auto`). They do **not** wrap `CompactLength`, so they don't need `unsendable` — a nice simplification over the existing types.

`AUTO` is a module-level constant (`Auto()`) for convenience. The `Auto` class is still needed for pattern matching syntax (`case Auto():`).

#### Naming: `Percent` vs `Percentage`

Use `Percent` because:
- It's shorter
- CSS reads as "50 percent" not "50 percentage"

### How They Replace the Old Types

The three old container types are deleted and replaced by unions:

| Removed Type | Replacement | Used By |
|---|---|---|
| `Dimension` | `Length \| Percent \| Auto` | `size_*`, `min_size_*`, `max_size_*`, `flex_basis` |
| `LengthPercentage` | `Length \| Percent` | `padding_*`, `border_*`, `gap_*` |
| `LengthPercentageAuto` | `Length \| Percent \| Auto` | `margin_*`, `inset_*` |

### Pattern Matching

With `__match_args__` defined on `Length` and `Percent`, structural pattern matching works naturally:

```python
match style.size_width:
    case Length(v):
        print(f"{v}px")
    case Percent(v):
        print(f"{v * 100}%")
    case Auto():
        print("auto")
```

### Style Constructor Changes

In the `.pyi` stub:

```python
class Style:
    def __init__(
        self,
        *,
        # Fields that accept length | percent | auto
        size_width: Length | Percent | Auto | None = None,
        # Fields that accept length | percent only
        padding_left: Length | Percent | None = None,
        # Fields that accept length | percent | auto
        margin_left: Length | Percent | Auto | None = None,
        ...
    ) -> None: ...
```

On the Rust side, this is implemented using `#[derive(FromPyObject)]` input enums that try each type in order:

```rust
#[derive(FromPyObject)]
enum DimensionInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
}

#[derive(FromPyObject)]
enum LengthPercentageInput {
    Length(Length),
    Percent(Percent),
}

#[derive(FromPyObject)]
enum LengthPercentageAutoInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
}
```

Each input enum has a `to_taffy()` method that converts to the appropriate taffy type.

### Style Getter Changes

Style getters return the new types:

```python
style.size_width      # → Length | Percent | Auto
style.padding_left    # → Length | Percent
style.margin_left     # → Length | Percent | Auto
```

On the Rust side, each getter inspects the inner taffy value's tag and returns the appropriate new type as a `PyObject`. For fields that can be auto, the getter checks `is_auto()` first, then distinguishes length vs percent via the tag. For `LengthPercentage` fields, only length and percent are possible.

### Helper Functions Removed

The old helper functions (`length()`, `percent()`, `auto()`, `zero()`) are deleted. The class constructors are equally concise:

| Old Helper | Replacement |
|---|---|
| `length(10)` | `Length(10)` |
| `percent(0.5)` | `Percent(0.5)` |
| `auto()` | `Auto()` or `AUTO` |
| `zero()` | `Length(0)` |

The constructors work for **all** Style fields — the key ergonomic win over the old API:

```python
Style(size_width=Length(10))        # ✓
Style(padding_left=Length(10))      # ✓ (was broken with old helpers!)
Style(margin_left=Length(10))       # ✓
Style(border_top=Percent(0.5))     # ✓ (was broken with old helpers!)
Style(inset_left=AUTO)             # ✓ (was broken with old helpers!)
```

## Design: Value Types for AvailableSpace

The same pattern applies to `AvailableSpace`, which has a type-narrowing problem:

```python
avail_w = available_space.width  # AvailableSpace
if avail_w.is_definite():
    v = avail_w.value()  # float | None — mypy can't narrow despite the guard
```

### New AvailableSpace Types

```python
class Definite:
    """A definite available space in pixels."""
    __match_args__ = ("value",)
    def __init__(self, value: float) -> None: ...
    @property
    def value(self) -> float: ...

class MinContent:
    """Min-content available space."""
    def __init__(self) -> None: ...

class MaxContent:
    """Max-content available space."""
    def __init__(self) -> None: ...

MIN_CONTENT: MinContent  # Module-level constant
MAX_CONTENT: MaxContent  # Module-level constant
```

### AvailableSpace Removal

The old `AvailableSpace` class is deleted. `AvailableDimensions` accepts and returns the new types directly:

```python
class AvailableDimensions:
    def __init__(
        self,
        width: Definite | MinContent | MaxContent,
        height: Definite | MinContent | MaxContent,
    ) -> None: ...

    @property
    def width(self) -> Definite | MinContent | MaxContent: ...
    @property
    def height(self) -> Definite | MinContent | MaxContent: ...
```

### Pattern Matching in Measure Functions

This solves the type-narrowing problem:

```python
def measure(known_dimensions, available_space, context):
    kw, kh = known_dimensions
    avail_w, avail_h = available_space

    match avail_w:
        case Definite(v):
            inline_size = v  # float — no Optional, no type: ignore
        case MinContent() | MaxContent():
            inline_size = len(context["text"]) * CHAR_WIDTH
```

### AvailableSpace Helper Functions Removed

Same rationale as the dimension helpers — the class constructors are equally concise:

| Old Helper | Replacement |
|---|---|
| `min_content()` | `MinContent()` or `MIN_CONTENT` |
| `max_content()` | `MaxContent()` or `MAX_CONTENT` |
| `AvailableSpace.definite(100)` | `Definite(100)` |

## Implementation Steps

### Step 1: Add `Length`, `Percent`, `Auto` types

In a new file `src/values.rs`:

- `Length` — `#[pyclass(frozen, module = "waxy")]` with `f32` field, `__init__`, `value` property, `__repr__`, `__eq__`, `__hash__`, `__match_args__`
- `Percent` — same structure
- `Auto` — `#[pyclass(frozen, module = "waxy")]` unit struct with `__init__`, `__repr__`, `__eq__`, `__hash__`
- `AUTO` — module-level constant via `m.add("AUTO", Auto {})?`

Register in `values::register()`, wire into `lib.rs`.

### Step 2: Add `Definite`, `MinContent`, `MaxContent` types

In the same `src/values.rs`:

- `Definite` — frozen pyclass with `f32` field, same methods as `Length`
- `MinContent` — frozen unit struct
- `MaxContent` — frozen unit struct
- `MIN_CONTENT` and `MAX_CONTENT` — module-level constants

### Step 3: Add input enums with `FromPyObject`

In `src/values.rs`, define the input enums:

```rust
#[derive(FromPyObject)]
pub enum DimensionInput { ... }

#[derive(FromPyObject)]
pub enum LengthPercentageInput { ... }

#[derive(FromPyObject)]
pub enum LengthPercentageAutoInput { ... }

#[derive(FromPyObject)]
pub enum AvailableSpaceInput { ... }
```

Each with `to_taffy()` methods that convert to the appropriate taffy type.

### Step 4: Update Style constructor

Change `set_field!` macro calls to use the new input enums instead of the old types:

```rust
// Before
set_field!("size_width", F_SIZE_WIDTH, |v: Dimension| {
    style.size.width = (&v).into()
});

// After
set_field!("size_width", F_SIZE_WIDTH, |v: DimensionInput| {
    style.size.width = v.to_taffy_dimension()
});
```

Remove the `use crate::dimensions::*` import from `style.rs`.

### Step 5: Update Style getters

Change getters to return the new types as `PyObject`:

```rust
// Before
#[getter]
fn get_size_width(&self) -> Dimension {
    self.inner.size.width.into()
}

// After
#[getter]
fn get_size_width(&self, py: Python<'_>) -> PyObject {
    dimension_to_value_type(py, self.inner.size.width)
}
```

Where `dimension_to_value_type` inspects the tag and returns `Length`, `Percent`, or `Auto`. Add similar helpers for `LengthPercentage` and `LengthPercentageAuto` fields.

### Step 6: Update `AvailableDimensions`

In `src/geometry.rs`:

- Constructor accepts `AvailableSpaceInput` (the new types)
- Properties return new types (`Definite`, `MinContent`, or `MaxContent`)
- `__iter__` yields new types

### Step 7: Delete old types and helpers

- Delete `src/dimensions.rs` entirely (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`)
- Delete `src/helpers.rs` entirely (`length`, `percent`, `auto`, `zero`, `min_content`, `max_content`, `fr`, `minmax`)
- Delete `AvailableSpace` from `src/enums.rs`
- Remove their registrations from `lib.rs`
- Remove from `python/waxy/__init__.py` exports

Note: `fr()` and `minmax()` are grid helpers unrelated to this issue. They could be kept as-is, or converted to `Fr(value)` / `GridTrack(min, max)` constructors in a future change. For now, keep them — move them into `src/grid.rs` or `src/values.rs`.

### Step 9: Update Python exports and stubs

- `python/waxy/__init__.py` — add new types to imports and `__all__`, remove old types
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style constructor/getter signatures, update helper return types, remove old type stubs

### Step 10: Update tests

- Delete `test_dimensions.py` (tests old types)
- Add new tests:
  - Construction and properties for each new type
  - `__repr__`, `__eq__`, `__hash__` for each
  - Pattern matching with `match`/`case`
  - `__match_args__` for positional destructuring
  - `AUTO`, `MIN_CONTENT`, `MAX_CONTENT` constants
  - Style construction with new types (all field categories)
  - Style getters return correct new types
  - `AvailableDimensions` with new types
  - Measure function using pattern matching on `AvailableDimensions`
- Update existing tests that use old types (in `test_style.py`, `test_integration.py`, `test_measure.py`, etc.)

### Step 11: Update CLAUDE.md

Update the architecture table and key design decisions to reflect the new types.

### Step 12: Run `just check`
