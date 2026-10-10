# Performance

These tips are for callers that lay out a tree every frame, like a terminal UI.
They're ordered by how much they save, largest first.
Savings are stated as ratios, since absolute times change with the machine and with every release.
The scripts behind each ratio are in the repository's
[`benchmarks/`](https://github.com/JoshKarpel/waxy/tree/main/benchmarks) directory;
run them against a release build (`uv run maturin develop --release`).

## Reuse one `TaffyTree` across frames

Building a new `TaffyTree` every frame throws away taffy's layout cache.
Keep one tree and update it instead,
with `set_style`, `set_children` and `set_node_context`.

Call `set_style` on every node every frame if that's simplest:
setting a style equal to the node's current one does nothing,
so the node keeps its cached layout and you don't need to diff styles yourself.
On a 39-node dashboard-shaped tree,
re-setting every style and recomputing costs about 2% of building and computing a new tree.

Call `set_node_context` only when a node's content actually changed.
A new context always marks the node dirty, since it has to be measured again,
and that dirties its ancestors too.
Changing one leaf's context on the same tree costs about 40% of building a new one.

## Memoize the measure callback on what changes its answer

Taffy calls the measure callback many times per leaf in one layout,
with `known_size` and `available_size` inputs that differ in ways your callback may ignore.
`compute_layout` already skips exact repeats for the same node within one call,
but only you know which differences matter.
For example, text measurement usually depends only on the text and one effective width
(`known_size.width`, else a definite available width, else none),
so a memo keyed on those two values answers every input that differs only elsewhere.

## Build styles once and merge them

Constructing a `Style` costs about four times as much as merging two with `|`.
Build the styles you reuse once, as module constants or cached functions,
and merge them per frame rather than constructing new ones.

## Reuse immutable values

Every value type is frozen, so one instance can be returned or passed again
instead of being rebuilt.
Returning a shared `Size` from a measure callback costs about a fifth of building a new one.

## Bind `Layout` fields to a local before reading them repeatedly

`margin`, `padding`, `border`, `location` and `size` build a new object on every access.
Binding `m = layout.margin` and reading its four sides costs about half as much as
reading `layout.margin.left`, `layout.margin.right` and so on.

## Pass small value types' arguments positionally

pyo3 matches keyword arguments by name at runtime,
so `Size(3.0, 4.0)` costs about two-thirds of `Size(width=3.0, height=4.0)`.
The same holds for `Point`, `KnownSize`, `AvailableSize` and `Length`.
