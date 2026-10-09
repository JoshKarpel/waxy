# Plan: Styling Foundations

This plan covers changes to waxy that make it a dependable base for counterweight's styling:
`Style` values whose equality matches how they merge,
errors for mistakes that are silently ignored today,
styles and trees that can be inspected,
and a `Rect` that means what taffy means by it.
It doesn't cover terminal concerns (cell geometry, border characters, text wrapping),
which belong in counterweight; see `plans/styling-foundations.md` in the counterweight repository.

The guiding principle: waxy mirrors taffy faithfully and exposes it cleanly to Python.
Anything taffy doesn't have, waxy adds only when it's generic to any taffy consumer.

## Release

All items ship together in `0.6.0`, before counterweight takes any of them up.
Items 1, 2 and 4 change observable behavior, so this is a breaking release; waxy is pre-1.0,
so a minor bump carries that.
Item 5b is gated on a measurement counterweight has to make and may ship in a later release.

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
set, since taffy doesn't keep the bitmask. After this change that result no longer equals the
style passed to `set_style`. Document it on `TaffyTree.style`.
Keeping a per-node bitmask table in `TaffyTree` would preserve the round trip, but it's extra
state that has to track node removal, and nothing currently depends on the round trip.

Tests (parametrized):

- Same values but different set fields compare unequal.
- Same values and same set fields compare equal and hash equal.
- A merge result equals a directly constructed style with the same set fields and values.

## 2. Reject unknown keyword arguments

`Style(flex_grw=1)` builds a style equal to `Style()` with no error.
The stubs catch this under mypy, but at runtime it's a silent no-op.

In `Style::new`, check every keyword against the known field names before extracting any
values, and raise `TypeError` with Python's usual wording:
`Style() got an unexpected keyword argument 'flex_grw'`.

The field names are spread across the `F_*` constants, the `set_field!` calls,
the `merge!` calls and the getters.
Add one constant table of `(name, flag)` pairs and use it for the unknown-key check,
`fields_set` and `__repr__` (item 3), so adding a field updates all three at once.

Tests: a misspelled keyword raises `TypeError` naming that keyword;
every documented field name is accepted.

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
  `taffy::Style::DEFAULT` rather than fields that were set.

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

`waxy.Line` has the same kind of geometry methods (`length`, `contains`, iteration),
and no waxy API takes or returns it. Grid placement uses waxy's own `GridPlacement`.
Remove `Line` entirely.

Update the stubs, the API docs and `tests/test_geometry.py`,
and list every removal under `Removed` in the changelog.

## 5. Support reusing a layout tree across frames

Counterweight builds a new `TaffyTree` every frame, which throws away taffy's layout cache.
Reusing one tree across frames needs `set_style`, `set_children`, `set_node_context` and
`mark_dirty`, all of which waxy already exposes. Two additions make reuse cheaper.

### 5a. Make `set_style` do nothing when the style is unchanged

Taffy's `set_style` marks the node dirty unconditionally (`TaffyTree::set_style`, in both taffy 0.9 and 0.14).
In `TaffyTree.set_style`, compare the new `inner` against the node's stored style and return
early when they're equal.
Compare `inner` rather than the full waxy `Style`, because taffy only ever sees `inner`.

This lets counterweight call `set_style` on every node every frame and keep taffy's cache for
everything that didn't change, with no style diffing of its own.

`set_node_context` also always marks the node dirty (`TaffyTree::set_node_context`). That's correct,
because a new context means the node has to be measured again. Counterweight should call it only
when a `Text` element actually changed. No waxy change is needed there.

Tests: after `compute_layout`, setting an equal style leaves `dirty(node)` false;
setting a different style makes it true.

### 5b. Return all layouts in one call (gated)

Add `TaffyTree.absolute_layouts(root) -> list[tuple[NodeId, Layout]]`: every node in the
subtree in pre-order, with `location` converted to absolute coordinates by adding up the
ancestors' locations.
Counterweight currently gets this by recursing in Python and calling `layout` and `children`
for every node.
Use the tree's rounding setting, the same as `layout()` does. Check that `layout()` returns
unrounded values when rounding is disabled before relying on that.

Gate: build this only if counterweight's measurement, which splits its "Calculated layout"
time into building the tree, computing it and reading results back, shows that reading results
back is a significant share.

## Out of scope

- Taffy's defaults. Waxy keeps `taffy::Style::DEFAULT` exactly; any terminal-friendly defaults
  are counterweight's choice.
- Caching text measurements. Taffy caches per node within a tree, and item 5 keeps that cache
  alive across frames.
- Rounding policy. Whether counterweight uses taffy's rounding or its own snapping is a
  counterweight decision; waxy already exposes `enable_rounding`, `disable_rounding`,
  `layout` and `unrounded_layout`.
