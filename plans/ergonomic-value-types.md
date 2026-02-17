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

Three separate problems:

1. **Verbosity**: `LengthPercentageAuto.length(10)` is painful to type. Users want `Length(10)`.
2. **Helpers are too narrow**: `length()`, `percent()`, `auto()` return `Dimension`, but many Style fields expect `LengthPercentage` or `LengthPercentageAuto`. There's no way to use the short helpers for padding, margin, border, gap, or inset fields.
3. **No pattern matching**: Dimension-like values are opaque objects. Users can call `is_auto()` but can't destructure them with Python 3.10+ `match`/`case`. Similarly, `AvailableSpace.value()` returns `float | None`, defeating mypy narrowing after `is_definite()` guards.

## Design: Standalone Value Types

Replace the "enum with static methods" pattern with standalone Python classes — one per variant. This is the "poor man's Rust enum" approach: model each variant as its own type and use `Union` on the Python side.

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
```

These are plain frozen pyclasses that store an `f32` (or nothing for `Auto`). They do **not** wrap `CompactLength`, so they don't need `unsendable` — a nice simplification over the existing types.

#### Naming: `Percent` vs `Percentage`

Use `Percent` because:
- It matches the existing `percent()` helper and `Dimension.percent()` method names
- It's shorter
- CSS reads as "50 percent" not "50 percentage"

### How They Map to Existing Types

The three existing container types become unions of the new types:

| Existing Type | Union Equivalent | Used By |
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

The Style constructor accepts both old and new types for full backward compatibility. In the `.pyi` stub:

```python
class Style:
    def __init__(
        self,
        *,
        # Fields that accept length | percent | auto
        size_width: Length | Percent | Auto | Dimension | None = None,
        # Fields that accept length | percent only
        padding_left: Length | Percent | LengthPercentage | None = None,
        # Fields that accept length | percent | auto
        margin_left: Length | Percent | Auto | LengthPercentageAuto | None = None,
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
    Legacy(Dimension),   // backward compat
}

#[derive(FromPyObject)]
enum LengthPercentageInput {
    Length(Length),
    Percent(Percent),
    Legacy(LengthPercentage),
}

#[derive(FromPyObject)]
enum LengthPercentageAutoInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
    Legacy(LengthPercentageAuto),
}
```

Each input enum has a `to_taffy()` method that converts to the appropriate taffy type.

### Style Getter Changes

Style getters return the new types instead of the old container types:

```python
# Before
style.size_width      # → Dimension
style.padding_left    # → LengthPercentage
style.margin_left     # → LengthPercentageAuto

# After
style.size_width      # → Length | Percent | Auto
style.padding_left    # → Length | Percent
style.margin_left     # → Length | Percent | Auto
```

On the Rust side, each getter inspects the inner taffy value's tag and returns the appropriate new type as a `PyObject`. For `Dimension`/`LengthPercentageAuto` fields, the getter checks `is_auto()` first, then distinguishes length vs percent via the tag. For `LengthPercentage` fields, only length and percent are possible.

This is a breaking change for code that depends on the exact return type (e.g., `isinstance(style.size_width, Dimension)`), but enables pattern matching on returned values.

### Helper Function Changes

The existing helpers change return types:

| Helper | Before | After |
|---|---|---|
| `length(value)` | `Dimension` | `Length` |
| `percent(value)` | `Dimension` | `Percent` |
| `auto()` | `Dimension` | `Auto` |
| `zero()` | `LengthPercentage` | `Length` |

Since the new types are accepted everywhere the old types were (via the input enums), this is backward-compatible at call sites:

```python
# Still works — Length is now accepted for all dimension-like Style fields
Style(size_width=length(10))        # was Dimension, now Length — still accepted
Style(padding_left=length(10))      # was broken! now works because Length is accepted
Style(margin_left=length(10))       # was Dimension, now Length — still accepted
```

This is the key ergonomic win: **`length()`, `percent()`, `auto()`, and `zero()` now work for all Style fields**, not just the ones that take `Dimension`.

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
```

### AvailableSpace Changes

`AvailableSpace` becomes a union type alias:

```python
type AvailableSpaceValue = Definite | MinContent | MaxContent
```

The existing `AvailableSpace` class remains for backward compatibility. Places that accept `AvailableSpace` (e.g., `AvailableDimensions.__init__`) also accept the new types. The `AvailableDimensions` properties return the new types.

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

### Helper Function Changes

| Helper | Before | After |
|---|---|---|
| `min_content()` | `AvailableSpace` | `MinContent` |
| `max_content()` | `AvailableSpace` | `MaxContent` |

A new `definite(value)` helper is also added for symmetry, returning `Definite`.

## Backward Compatibility

### What Still Works

- Old types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`, `AvailableSpace`) remain as classes
- Old static methods (`Dimension.length()`, `Dimension.auto()`, etc.) still work
- Old types are still accepted by Style constructor and other APIs
- Existing test code continues to pass without changes

### What Changes (Breaking)

- Helper function return types change (e.g., `length()` returns `Length` instead of `Dimension`). Call sites that pass these to Style fields still work, but code that does `isinstance(length(10), Dimension)` would break.
- Style getter return types change (e.g., `style.size_width` returns `Length | Percent | Auto` instead of `Dimension`). Code that does `isinstance(style.size_width, Dimension)` would break.
- `AvailableDimensions.width`/`.height` return new types instead of `AvailableSpace`.

### Deprecation Path

The old container types (`Dimension`, `LengthPercentage`, `LengthPercentageAuto`) should be deprecated in favor of the new value types. They can be removed in a future major version. `AvailableSpace` follows the same path.

Given that waxy is pre-1.0, these breaking changes are acceptable.

## Implementation Steps

### Step 1: Add `Length`, `Percent`, `Auto` types

In a new file `src/values.rs`:

- `Length` — `#[pyclass(frozen, module = "waxy")]` with `f32` field, `__init__`, `value` property, `__repr__`, `__eq__`, `__hash__`, `__match_args__`
- `Percent` — same structure
- `Auto` — `#[pyclass(frozen, module = "waxy")]` unit struct with `__init__`, `__repr__`, `__eq__`, `__hash__`

Register in `values::register()`, wire into `lib.rs`.

### Step 2: Add `Definite`, `MinContent`, `MaxContent` types

In the same `src/values.rs`:

- `Definite` — frozen pyclass with `f32` field, same methods as `Length`
- `MinContent` — frozen unit struct
- `MaxContent` — frozen unit struct

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

Each with `to_taffy()` methods.

### Step 4: Update Style constructor

Change `set_field!` macro calls to use the new input enums instead of the old types. For example:

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

Where `dimension_to_value_type` inspects the tag and returns `Length`, `Percent`, or `Auto`.

### Step 6: Update `AvailableDimensions`

- Constructor accepts `AvailableSpaceInput` (new types + legacy `AvailableSpace`)
- Properties return new types (`Definite`, `MinContent`, or `MaxContent`)
- `__iter__` yields new types

### Step 7: Update helper functions

In `src/helpers.rs`:

- `length()` → returns `Length`
- `percent()` → returns `Percent`
- `auto()` → returns `Auto`
- `zero()` → returns `Length` (with value `0.0`)
- `min_content()` → returns `MinContent`
- `max_content()` → returns `MaxContent`
- Add `definite(value)` → returns `Definite`

### Step 8: Update Python exports

- `python/waxy/__init__.py` — add new types to imports and `__all__`
- `python/waxy/__init__.pyi` — add type signatures for new types, update Style constructor/getter signatures, update helper return types

### Step 9: Add tests

- Construction and properties for each new type
- `__repr__`, `__eq__`, `__hash__` for each
- Pattern matching with `match`/`case`
- `__match_args__` for positional destructuring
- Style construction with new types (all field categories)
- Style construction with mixed old and new types (backward compat)
- Style getters return new types
- Helper functions return new types and are accepted by all Style fields
- `AvailableDimensions` with new AvailableSpace types
- Measure function using pattern matching on `AvailableDimensions`

### Step 10: Run `just check`

## Questions to Resolve

1. **Should `Auto` be a singleton?** We could expose an `AUTO` module-level constant as `Auto()` for convenience. Pattern matching still uses `case Auto():` regardless. The class is still needed for the pattern match syntax.

2. **Should we add `__match_args__` to the old types too?** Adding `__match_args__` to `Dimension`, `LengthPercentage`, `LengthPercentageAuto` would enable limited pattern matching even for users who haven't migrated. But it may not be worth the effort if we're deprecating them.

3. **Should `AvailableSpace` decomposition be a separate issue?** It follows the same pattern as the dimension types but affects different APIs (measure functions vs. style construction). Could be split into a Phase 2 if the dimension work is large enough on its own.
