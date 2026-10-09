# Plan: Styling Foundations

This plan covers changes to waxy that make it a dependable base for counterweight's styling:
`Style` values whose equality matches how they merge,
errors for mistakes that are silently ignored today,
styles and trees that can be inspected,
a `Rect` that means what taffy means by it,
and styles and layout trees cheap enough to build, hash and reuse every frame.
It doesn't cover terminal concerns (cell geometry, border characters, text wrapping),
which belong in counterweight; see `plans/styling-foundations.md` in the counterweight repository.

The guiding principle: waxy mirrors taffy faithfully and exposes it cleanly to Python.
Anything taffy doesn't have, waxy adds only when it's generic to any taffy consumer.

## Release

All ungated items ship together in `0.6.0`, before counterweight takes any of them up.
Items 1, 2, 4 and 5a change observable behavior, so this is a breaking release;
waxy is pre-1.0, so a minor bump carries that.
Item 5b is gated on a measurement counterweight has to make and may ship in a later release.

No released counterweight version depends on waxy, so nothing published breaks.
Counterweight's `main` still calls `Rect.contains` (`app.py:407`);
its plan removes that before it raises its floor to `waxy>=0.6.0`.

## 1. Make `Style` equality match merge behavior

`Style.__eq__` and `__hash__` compare only the underlying `taffy::Style`,
but `|` also depends on which fields were explicitly set (the `set_fields` bitmask).
Two styles can compare equal and still merge differently:

```text
Style() == Style(flex_grow=0)                       -> True, same hash
(Style(flex_grow=3) | Style()).flex_grow            -> 3.0
(Style(flex_grow=3) | Style(flex_grow=0)).flex_grow -> 0.0
```

Any cache keyed on style equality can therefore return the wrong merge.

Change `__eq__` to compare both `inner` and `set_fields`, and mix `set_fields` into `__hash__`.

`TaffyTree.style(node)` builds a `Style` from the stored `taffy::Style` and marks every field as
set, since taffy doesn't keep the bitmask.
It does that with `set_fields: u64::MAX` (`From<&taffy::Style>` in `src/style.rs`),
which also sets bits 60 to 63, where there are no fields.
Once equality compares `set_fields`, that result wouldn't even equal a `Style` with every field
passed explicitly.
Replace `u64::MAX` with an `ALL_FIELDS` mask built from item 2's field table.

Even with the mask, `tree.style(node)` no longer equals the style passed to `set_style`
unless every field was set. Document it on `TaffyTree.style`.
Keeping a per-node bitmask table in `TaffyTree` would preserve the round trip, but it's extra
state that has to track node removal, and nothing currently depends on the round trip.

Tests (parametrized):

- Same values but different set fields compare unequal.
- Same values and same set fields compare equal and hash equal.
- A merge result equals a directly constructed style with the same set fields and values.
- `tree.style(node)` equals a `Style` constructed with every field passed explicitly.

## 2. Reject unknown keyword arguments

`Style(flex_grw=1)` builds a style equal to `Style()` with no error.
The stubs catch this under mypy, but at runtime it's a silent no-op.

`Style::new` looks up every known field name in `kwargs`, so a key it doesn't know is never
looked at.
Invert that: iterate over the keywords actually passed and `match` each key to its field's
extraction, with a final arm that raises `TypeError` in the wording pyo3 uses for its own
signatures: `Style.__new__() got an unexpected keyword argument 'flex_grw'`.
The unknown-key check and extraction are then the same `match`, so they can't drift apart,
and construction does work in proportion to the fields passed rather than all of them
(item 7).

The field names are also spread across the `F_*` constants, the `merge!` calls and the getters.
Add one constant table of `(name, flag)` pairs, in declaration order,
and use it for `ALL_FIELDS` (item 1), `fields_set` and `__repr__` (item 3).
The table can't drive extraction or merging, since each field converts differently,
so adding a field still means touching the `F_*` constant, the `match` arm, `merge!`,
the getter, `__hash__`, the stub and the table.

Nothing type-checks the table against the `match` arms or the getters.
Guard it with a test over every property on `Style`:
`Style(**{p: getattr(Style(), p)}).fields_set == {p}`.
That holds for every field, since non-`Option` getters never return `None`
and an explicit `None` for an `Option` field counts as set.
It catches a table entry without a `match` arm (the constructor raises),
a `match` arm without a table entry (`fields_set` misses it),
and a getter without either.

Tests: a misspelled keyword raises `TypeError` naming that keyword;
the per-property round trip above.

## 3. Make styles and trees inspectable

`repr(Style(...))` always prints `Style(display=Flex, position=Relative)`,
whatever was set, so a style can't show its own contents while you debug.

- **`Style.fields_set -> frozenset[str]`**: the names of the explicitly set fields.
  The name follows pydantic's `model_fields_set`.
- **`Style.__repr__`**: list the set fields in declaration order, each with its getter's repr,
  e.g. `Style(flex_grow=1.0, border_top=Length(1))`. An empty style prints `Style()`.
- **`TaffyTree.format_tree(root) -> str`**: an indented dump of the subtree, giving each node's
  id, computed location and size, and its style.
  Taffy's `print_tree` writes to stdout with `println!`, which corrupts the screen of a running
  TUI, so waxy does its own traversal and returns the string. Keep `print_tree` as is.
  Stored styles have no bitmask (see item 1), so the dump shows fields that differ from
  `taffy::Style::DEFAULT` rather than fields that were set:
  compute that mask, build a `Style` with it, and reuse `__repr__`.

Tests: `repr` round-trips through `eval` (with waxy's names in scope) for representative styles,
since every value type's repr is already constructor syntax;
`fields_set` matches the keywords passed in and the union of set fields after `|`;
`format_tree` includes every node in a small nested tree.

## 4. Return `Rect` to taffy's meaning and remove `Line`

In taffy, `Rect<T>` is a container with one value per side.
Taffy uses it for margin, padding and border thicknesses, and waxy returns it that way from
`Layout.margin`, `Layout.padding` and `Layout.border`.
Waxy also gives `Rect` geometry methods that treat the four fields as edge coordinates of a box
(a closed interval). Taffy has no counterpart for that, and on a per-side value the methods are
meaningless.
Counterweight is the only consumer of the geometry methods, and it's moving to its own integer
grid type.

Remove from `Rect`:

- `width`, `height`, `size`
- `contains`
- `top_left`, `top_right`, `bottom_left`, `bottom_right`, `corners`
- `top_edge`, `bottom_edge`, `left_edge`, `right_edge`
- `points`, `rows`, `columns`, `__iter__`, `__len__`
- `intersection`

Remove the `PixelIter`, `RowIter` and `ColumnIter` classes.
`Rect` keeps its four fields, `__eq__`, `__hash__` and `__repr__`.

`waxy.Line` is an `f32` interval with the same kind of geometry methods
(`length`, `contains`, iteration).
Taffy's own `Line<T>` is a start/end container (it's what `grid_row` and `grid_column` hold),
but waxy exposes those through `GridPlacement`, and no waxy API takes or returns `waxy.Line`.
Remove `Line` entirely.

Update the stubs, the API docs and `tests/test_geometry.py`,
and list every removal under `Removed` in the changelog.

## 5. Support reusing a layout tree across frames

Counterweight builds a new `TaffyTree` every frame, which throws away taffy's layout cache.
Reusing one tree across frames needs `set_style`, `set_children`, `set_node_context` and
`mark_dirty`, all of which waxy already exposes. Two additions make reuse cheaper.

### 5a. Make `set_style` do nothing when the style is unchanged

Taffy's `set_style` marks the node dirty unconditionally (`TaffyTree::set_style`).
In `TaffyTree.set_style`, compare the new `inner` against the node's stored style and return
early when they're equal.
Compare `inner` rather than the full waxy `Style`, because taffy only ever sees `inner`.

This lets counterweight call `set_style` on every node every frame and keep taffy's cache for
everything that didn't change, with no style diffing of its own.

This is a breaking change: calling `set_style` with an equal style no longer forces a relayout.
Document it on `TaffyTree.set_style`, and add a changelog `Changed` entry that points to
`mark_dirty` for forcing one.

`set_node_context` also always marks the node dirty (`TaffyTree::set_node_context`). That's correct,
because a new context means the node has to be measured again. Counterweight should call it only
when a `Text` element actually changed. No waxy change is needed there.

Tests: after `compute_layout`, setting an equal style leaves `dirty(node)` false;
setting a different style makes it true.

### 5b. Return all layouts in one call (gated)

Add `TaffyTree.absolute_layouts(root) -> list[tuple[NodeId, Point, Layout]]`:
every node in the subtree in pre-order, with its absolute position
(the sum of its own and its ancestors' locations) and its `Layout` unchanged.
Keep the absolute position out of `Layout`:
everywhere else `Layout.location` is relative to the parent,
and a `Layout` whose `location` means something else is the same overloading item 4 removes
from `Rect`.
Counterweight currently gets this by recursing in Python and calling `layout` and `children`
for every node.

Use the tree's rounding setting, the same as `layout()` does:
taffy's `layout()` returns the rounded layout when rounding is enabled and the unrounded one
otherwise.
Summing rounded relative locations gives the rounded absolute position,
because taffy rounds each node against its cumulative absolute coordinates
rather than its relative location.
Pin that with a test on a tree with fractional sizes.

Gate: build this only if counterweight's measurement, which splits its "Calculated layout"
time into building the tree, computing it and reading results back, shows that reading results
back is a significant share.

## 6. Cache `Style`'s hash

`Style` is frozen, so its hash can be computed once and stored.
Measured on a release build (`timeit`, best of 5 runs of 1,000,000 `hash()` calls):

| Style | Uncached | Cached |
|---|---|---|
| `Style()` | 454 ns | 53 ns |
| Typical (11 fields) | 408 ns | 53 ns |
| Grid with 7 template tracks | 611 ns | 53 ns |

For comparison, a 10-field frozen dataclass hashes in 175 ns.

The cache costs nothing measurable elsewhere
(best of 7 runs of 300,000 calls, typical style):

| Operation | Uncached | Cached |
|---|---|---|
| Construct | 4425 ns | 4326 ns |
| Merge (`a \| b`) | 211 ns | 197 ns |
| Merge, then first hash | 595 ns | 584 ns |
| `sys.getsizeof(Style)` | 592 bytes | 608 bytes |

The time differences are within run-to-run noise,
and the 16 bytes are about 3% of a `Style`.

The cache only pays when the same `Style` object is hashed more than once,
which counterweight doesn't do yet:
a headless run of its `dashboard.py` and `canvas.py` workloads,
with `Style.__hash__` patched to hash `layout` as counterweight's plan step 2 does,
made zero `waxy.Style` hashes.
Its plan step 3 (one merge rule) may add a merge cache keyed on `(self, other)`;
utility styles like `pad(1)` are `lru_cache`d and merge results come back from the cache,
so the same objects would then be hashed every frame.
Since the cache is free, it ships now rather than waiting for that.

Implementation:

- Add a `std::cell::OnceCell<u64>` field (`Style` is `unsendable`, so it needn't be `Sync`).
- Move the hash body into a `compute_hash` method in the plain `impl Style` block
  (beside `to_taffy`), outside `#[pymethods]`,
  and have `__hash__` return `get_or_init(compute_hash)`.
- Never mutate a `Style` after construction, so a cached hash can't go stale.
  Today `__or__` clones `self` and mutates the clone, which would copy the cached hash.
  Instead, clone only `self.inner`, merge into it,
  and build the result through a single `Style::from_parts(inner, set_fields)` constructor
  that every construction path uses and that is the only place the cell is created.

Tests: a merge result whose left operand was hashed first
hashes equal to a directly constructed equal style.

## 7. Make `Style` construction cheap

Constructing a `Style` costs far more than merging or hashing one.
Measured on a release build (`timeit`, best of 5 runs of 200,000 calls):

| Call | Now | Interned keys | Interned keys + cast-based extraction |
|---|---|---|---|
| `Style()` | 151 ns | 174 ns | 161 ns |
| `Style(not_a_field=1)` | 3249 ns | 651 ns | 618 ns |
| `Style(flex_grow=1)` | 3163 ns | 724 ns | 661 ns |
| `Style(size_width=Length(1))` | 3429 ns | 660 ns | 635 ns |
| `Style(size_width=Percent(1.0))` | 4051 ns | 1605 ns | 667 ns |
| `Style(size_width=AUTO)` | 4717 ns | 2237 ns | 684 ns |
| Typical (11 fields) | 4425 ns | | 1259 ns |

Two costs account for it.

- **A fixed cost for checking every field name.** `Style::new` calls `kwargs.get_item("…")` for
  all 59 fields, and each call builds a Python string from the Rust literal before looking it
  up. Interning the keys (`pyo3::intern!`) removed most of it, from about 3.1 µs to 0.5 µs.
  The rest is 59 lookups that mostly miss; item 2's dispatch over the passed keywords removes
  those too, leaving work in proportion to the fields passed.
- **A per-field cost that grows with the variant's position in its union.**
  `#[derive(FromPyObject)]` on an enum tries each variant in order and builds a `PyErr` with a
  formatted message for every miss, so `AUTO`, the third `DimensionInput` variant, cost 1.5 µs
  more than `Length`, the first.
  A hand-written `extract` that tries `obj.cast::<T>()` per variant builds no error until every
  variant has missed, and made every variant cost the same.

Replace `#[derive(FromPyObject)]` on all the `*Input` enums in `src/values.rs` with one
declarative macro that generates the enum and a cast-based `FromPyObject` from a single variant
list, so the accepted types are still written once.
Two variant kinds need support:
a pyclass, checked with `cast`, and a nested input
(`FlexBasisInput::Dimension(DimensionInput)`, `GridTemplateInput::Track(GridTrackInput)`,
`RepetitionCountInput::Count(u16)`), tried with its own `extract`.
When every variant misses, raise one `TypeError` naming the accepted types and the type received,
e.g. `expected Length | Percent | Auto | ..., got int`.
This replaces pyo3's multi-line per-variant message, which no test matches on.

The extractors serve every constructor that takes a value union, not only `Style`:
`AvailableSize`, grid tracks, `Repeat` and grid placements share them.

Counterweight builds most of its styles once (module constants and `lru_cache`d utilities like
`pad(1)`), so its per-frame cost is merging and, after item 6, hashing.
Construction matters to callers that build styles per frame from changing values,
which a style API invites.

Tests: each variant of each union extracts to the right value
(parametrized, so a variant missing from the macro list fails);
a value of the wrong type raises `TypeError` naming the accepted types.

## Out of scope## Out of scope

- Taffy's defaults. Waxy keeps `taffy::Style::DEFAULT` exactly; any terminal-friendly defaults
  are counterweight's choice.
- Caching text measurements. Taffy caches per node within a tree, and item 5 keeps that cache
  alive across frames.
- Rounding policy. Whether counterweight uses taffy's rounding or its own snapping is a
  counterweight decision; waxy already exposes `enable_rounding`, `disable_rounding`,
  `layout` and `unrounded_layout`.
