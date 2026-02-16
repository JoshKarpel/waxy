# Plan: Custom Measure Functions and Node Context (Issue #18)

## Background

Taffy's `TaffyTree<NodeContext>` is generic over a node context type. Currently, waxy uses `TaffyTree<()>` (the default — no context). To support measure functions, we need to:

1. Change the inner tree to `TaffyTree<PyObject>` so any Python object can be attached as node context
2. Expose methods for managing node context
3. Expose `compute_layout_with_measure`, which accepts a Python callable

### How Measure Functions Work in Taffy

During layout, when taffy encounters a **leaf node** (no children), it needs to know how big that node's content is. Without a measure function, leaf nodes have zero intrinsic size — they're sized entirely by their style (explicit `width`/`height`, flex-grow, etc.).

A measure function lets you say: "this leaf contains text/an image/a widget — here's how to compute its intrinsic size given the available space." Taffy calls the measure function with:

- **known_dimensions**: `Size<Option<f32>>` — if the layout algorithm already determined width or height (e.g., from an explicit style), those values are `Some`. The measure function should respect these.
- **available_space**: `Size<AvailableSpace>` — how much space the parent is offering (definite px, min-content, or max-content)
- **node_id**: which node is being measured
- **node_context**: the `Option<&mut NodeContext>` attached to this node (the user's custom data)
- **style**: the node's style

The function returns a `Size<f32>` — the measured (width, height).

**Node context** is arbitrary user data attached to a node. For example, a text node might store `{"text": "Hello world", "font_size": 14}`, and the measure function would use that to calculate how much space the text needs at a given width.

### Why Waxy Auto-Skips Nodes Without Context

Taffy calls the measure function for **all leaf nodes**, including those without context. The `node_context` parameter will be `None` for nodes that have no context set. Taffy does not auto-skip because it's a generic Rust library that leaves this policy to the caller.

However, in practice, **every taffy example returns `Size::ZERO` for `None` context**. From taffy's own `examples/measure.rs`:

```rust
match node_context {
    None => Size::ZERO,
    Some(NodeContext::Text(text_context)) => { /* measure text */ }
    Some(NodeContext::Image(image_context)) => { /* measure image */ }
}
```

This makes sense: the measure function reports **intrinsic content size**, and without context there is no content to measure. Style-based sizing (explicit `width`/`height`, min/max constraints, padding, border) is handled by `compute_leaf_layout` *around* the measure function's return value — it's not the measure function's job.

Additional details from the taffy source (`src/compute/leaf.rs`):

- During `RunMode::ComputeSize` (sizing flex/grid children), if **both** dimensions are already known from style, taffy short-circuits and doesn't call the measure function at all (lines 92–108).
- During `RunMode::PerformLayout` (full layout pass), the measure function is **always called** with `known_dimensions = Size::NONE` (both `None`), regardless of context.
- Only leaf nodes (no children) ever reach the measure function path — the dispatch in `taffy_tree.rs` matches `(_, false)` for `has_children == false`.

In waxy, the Rust closure returns `Size::ZERO` for nodes without context **before calling Python**. This means:
- The user's measure function is **only called when context is present**
- The context parameter is always `T`, not `T | None`
- This eliminates boilerplate and enables the `Generic[T]` type safety on `TaffyTree`
- No edge cases are lost — a leaf without context has no content, so zero intrinsic size is always correct

## New Types

### `KnownDimensions`

A frozen `#[pyclass]` in `src/geometry.rs` that wraps taffy's `Size<Option<f32>>` — the independently-optional width/height that taffy passes to measure functions. Our existing `Size<f32>` can't represent this because it requires both dimensions to be present.

```rust
#[pyclass(frozen, module = "waxy")]
pub struct KnownDimensions {
    width: Option<f32>,
    height: Option<f32>,
}
```

Implements `__iter__` so it can be unpacked: `known_width, known_height = known_dimensions`.

### `AvailableDimensions`

A frozen `#[pyclass]` in `src/geometry.rs` that wraps `Size<AvailableSpace>` — the available space in each axis passed to measure functions.

```rust
#[pyclass(frozen, unsendable, module = "waxy")]
pub struct AvailableDimensions {
    width: AvailableSpace,
    height: AvailableSpace,
}
```

`unsendable` because `AvailableSpace` wraps taffy types that contain `CompactLength`. Implements `__iter__` so it can be unpacked: `avail_width, avail_height = available_space`.

## Implementation Plan

### Step 1: Change `TaffyTree` to use `PyObject` context

In `src/tree.rs`, change:
```rust
inner: tp::TaffyTree,        // currently TaffyTree<()>
```
to:
```rust
inner: tp::TaffyTree<PyObject>,
```

This is backwards-compatible — existing code that doesn't use contexts still works fine (nodes just have no context attached).

### Step 2: Add `KnownDimensions` and `AvailableDimensions`

In `src/geometry.rs`, add both types with:
- `__init__` constructor
- `width` / `height` properties
- `__repr__`, `__eq__`
- `__iter__` (yields width then height, for unpacking)
- `From` conversions to/from taffy types

Register them in `geometry::register()`.

### Step 3: Add `new_leaf_with_context`

```rust
fn new_leaf_with_context(&mut self, style: &Style, context: PyObject) -> PyResult<NodeId>
```

Wraps `taffy::TaffyTree::new_leaf_with_context`.

### Step 4: Add `set_node_context` / `get_node_context`

```rust
fn set_node_context(&mut self, node: &NodeId, context: Option<PyObject>) -> PyResult<()>
fn get_node_context(&self, node: &NodeId) -> Option<PyObject>
```

`get_node_context` clones the `PyObject` (which is just an `Arc<PyObject>` ref-count bump under the hood).

### Step 5: Add `compute_layout_with_measure`

```rust
fn compute_layout_with_measure(
    &mut self,
    py: Python<'_>,
    node: &NodeId,
    available_width: Option<&AvailableSpace>,
    available_height: Option<&AvailableSpace>,
    measure: PyObject,  // a Python callable
) -> PyResult<()>
```

This calls `taffy::TaffyTree::compute_layout_with_measure` with a Rust closure that:
1. Checks if `node_context` is `None` — if so, returns `Size::ZERO` immediately (no Python call)
2. Converts the taffy arguments to waxy Python types (`KnownDimensions`, `AvailableDimensions`, etc.)
3. Calls the Python `measure` callable
4. Converts the returned `Size` back to `taffy::Size<f32>`

The closure signature adapting taffy → Python:
```rust
|known_dimensions, available_space, node_id, node_context, style| {
    // If no context, return zero — don't bother calling Python
    let Some(context) = node_context else {
        return Ok(taffy::Size::ZERO);
    };
    // Convert to Python types and call the Python function
}
```

**Measure function signature** (from the user's perspective):

```python
def my_measure(
    known_dimensions: KnownDimensions,
    available_space: AvailableDimensions,
    node_id: NodeId,
    node_context: T,  # always present — never None
    style: Style,
) -> Size:
    ...
```

The measure function always returns a `Size` (no tuple fallback).

### Step 6: Update Python exports

- `python/waxy/__init__.py` — add `KnownDimensions` and `AvailableDimensions` exports
- `python/waxy/__init__.pyi` — add type signatures for new types and methods, with `TaffyTree` made generic over `T`

**Generic `TaffyTree[T]`** in the `.pyi`:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class TaffyTree(Generic[T]):
    def new_leaf_with_context(self, style: Style, context: T) -> NodeId: ...
    def get_node_context(self, node: NodeId) -> T | None: ...
    def set_node_context(self, node: NodeId, context: T | None) -> None: ...
    def compute_layout_with_measure(
        self,
        node: NodeId,
        *,
        measure: Callable[[KnownDimensions, AvailableDimensions, NodeId, T, Style], Size],
        available_width: AvailableSpace | None = None,
        available_height: AvailableSpace | None = None,
    ) -> None: ...
    # ... all existing methods unchanged ...
```

This way mypy enforces that the measure function's context type matches what's stored in the tree.

### Step 7: Add tests

Test cases:
- `new_leaf_with_context` creates a node with context
- `get_node_context` returns the context
- `set_node_context` updates/clears context
- `KnownDimensions` — construction, properties, unpacking via iteration
- `AvailableDimensions` — construction, properties, unpacking via iteration
- `compute_layout_with_measure` with a simple fixed-size measure function
- `compute_layout_with_measure` with a text-like measure function that responds to available width
- Measure function receives correct `known_dimensions` when style has explicit size
- Measure function is NOT called for nodes without context (they get zero size automatically)
- Error handling: measure function raises an exception → propagated to caller

## Usage Examples

### Example 1: Fixed-Size Leaf (e.g., an image)

```python
from waxy import TaffyTree, Style, Size, Display, FlexDirection, KnownDimensions, length

tree: TaffyTree[dict] = TaffyTree()

# Create a leaf node with context describing an image
image_node = tree.new_leaf_with_context(
    Style(),
    {"type": "image", "intrinsic_width": 400.0, "intrinsic_height": 300.0},
)

# Container with a fixed width
root = tree.new_with_children(
    Style(display=Display.Flex, size_width=length(200)),
    [image_node],
)

# Define how to measure leaf nodes
# `context` is always present — nodes without context get Size(0, 0) automatically
def measure(known_dimensions, available_space, node_id, context, style):
    kw, kh = known_dimensions
    if kw is not None and kh is not None:
        return Size(kw, kh)

    if context["type"] == "image":
        w = context["intrinsic_width"]
        h = context["intrinsic_height"]
        if kw is not None:
            return Size(kw, kw / w * h)  # scale height to match
        if kh is not None:
            return Size(kh / h * w, kh)  # scale width to match
        return Size(w, h)

    return Size(0, 0)

tree.compute_layout_with_measure(root, measure=measure)

layout = tree.layout(image_node)
print(layout.size)  # Size(width=200.0, height=150.0) — scaled to fit 200px wide
```

### Example 2: Text Wrapping

```python
import textwrap

from waxy import TaffyTree, Style, Size, Display, FlexDirection, length, AvailableSpace

tree: TaffyTree[dict] = TaffyTree()

text_node = tree.new_leaf_with_context(
    Style(),
    {"type": "text", "content": "Hello world, this is some long text that should wrap"},
)

root = tree.new_with_children(
    Style(display=Display.Flex, size_width=length(100)),
    [text_node],
)

CHAR_WIDTH = 8.0
CHAR_HEIGHT = 16.0

def measure(known_dimensions, available_space, node_id, context, style):
    kw, kh = known_dimensions
    if kw is not None and kh is not None:
        return Size(kw, kh)

    if context["type"] != "text":
        return Size(0, 0)

    text = context["content"]
    avail_w, _ = available_space

    # Determine available inline size
    if kw is not None:
        inline_size = kw
    elif avail_w.is_definite():
        inline_size = avail_w.value()
    else:
        # No constraint — lay out on a single line
        inline_size = len(text) * CHAR_WIDTH

    # Wrap text to fit within inline_size
    chars_per_line = max(1, int(inline_size / CHAR_WIDTH))
    lines = textwrap.wrap(text, width=chars_per_line)
    line_count = max(1, len(lines))

    return Size(inline_size, line_count * CHAR_HEIGHT)

tree.compute_layout_with_measure(root, measure=measure)
layout = tree.layout(text_node)
print(layout.size)  # Text wrapped within 100px width
```

### Example 3: Multiple Node Types with Shared Measure Function

```python
from waxy import TaffyTree, Style, Size, Display, FlexDirection, length

tree: TaffyTree[dict] = TaffyTree()

# Different node types, same tree
heading = tree.new_leaf_with_context(Style(), {"type": "text", "content": "Title", "font_size": 24})
body = tree.new_leaf_with_context(Style(), {"type": "text", "content": "Body text here", "font_size": 14})
avatar = tree.new_leaf_with_context(Style(), {"type": "image", "width": 48, "height": 48})

root = tree.new_with_children(
    Style(display=Display.Flex, flex_direction=FlexDirection.Column, size_width=length(300)),
    [heading, body, avatar],
)

def measure(known_dimensions, available_space, node_id, ctx, style):
    kw, kh = known_dimensions
    if kw is not None and kh is not None:
        return Size(kw, kh)
    if ctx["type"] == "image":
        return Size(ctx["width"], ctx["height"])
    if ctx["type"] == "text":
        # Simple: each char is font_size * 0.6 wide, one line
        char_w = ctx["font_size"] * 0.6
        w = len(ctx["content"]) * char_w
        return Size(w, float(ctx["font_size"]))
    return Size(0, 0)

tree.compute_layout_with_measure(root, measure=measure)

# Each node now has a layout computed using its context
for node in [heading, body, avatar]:
    print(tree.layout(node).size)
```

### Example 4: Updating Context After Creation

```python
tree: TaffyTree[dict] = TaffyTree()
node = tree.new_leaf_with_context(Style(), {"text": "Hello"})

# Later, update the text
tree.set_node_context(node, {"text": "Hello, world!"})
# This also marks the node as dirty, so the next compute_layout will re-measure it

# Or remove the context entirely
tree.set_node_context(node, None)
print(tree.get_node_context(node))  # None
```

## Resolved Questions

1. **`known_dimensions` representation**: `KnownDimensions(width: float | None, height: float | None)` — a frozen pyclass with `__iter__` for unpacking (`kw, kh = known_dimensions`).

2. **`available_space` representation**: `AvailableDimensions(width: AvailableSpace, height: AvailableSpace)` — same pattern as `KnownDimensions`, with `__iter__` for unpacking.

3. **Return type**: Always `Size`. No tuple fallback.

4. **Error propagation**: If the Python measure function raises, the exception propagates out of `compute_layout_with_measure` as a Python exception. PyO3 supports this naturally.

5. **`compute_layout` (without measure) still works**: Yes. The existing `compute_layout` method stays as-is. Leaf nodes without a measure function simply have zero intrinsic size (taffy's default behavior). Users opt in to measure functions by calling `compute_layout_with_measure` instead. The key difference: `compute_layout_with_measure` wraps the user's measure function so that **nodes without context automatically get `Size(0, 0)` without the user's function being called**. This eliminates the boilerplate of checking for `None` context in every measure function.

6. **Generic `TaffyTree[T]`**: The `.pyi` stub uses `Generic[T]` so mypy enforces that the context type flows through to `new_leaf_with_context`, `get_node_context`, `set_node_context`, and the measure function's `node_context` parameter. Since nodes without context are handled automatically, the measure function receives `T` (not `T | None`).
