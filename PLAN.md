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

### Step 2: Add `new_leaf_with_context`

```rust
fn new_leaf_with_context(&mut self, style: &Style, context: PyObject) -> PyResult<NodeId>
```

Wraps `taffy::TaffyTree::new_leaf_with_context`.

### Step 3: Add `set_node_context` / `get_node_context`

```rust
fn set_node_context(&mut self, node: &NodeId, context: Option<PyObject>) -> PyResult<()>
fn get_node_context(&self, node: &NodeId) -> Option<PyObject>
```

`get_node_context` clones the `PyObject` (which is just an `Arc<PyObject>` ref-count bump under the hood).

### Step 4: Add `compute_layout_with_measure`

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
1. Converts the taffy arguments to waxy Python types
2. Calls the Python `measure` callable
3. Converts the returned Python `Size` (or `(width, height)` tuple) back to `taffy::Size<f32>`

The closure signature adapting taffy → Python:
```rust
|known_dimensions, available_space, node_id, node_context, style| {
    // Convert to Python types and call the Python function
}
```

**For `known_dimensions`**: Pass as a Python `Size` where we use `float('inf')` or a special sentinel... Actually, the cleanest approach: pass `(Optional[float], Optional[float])` — a tuple of `(width, height)` where each can be `None`. This matches taffy's `Size<Option<f32>>` directly.

**Decision**: The measure function receives a `MeasureArgs` dataclass-like object (or we just pass positional args). Positional args are simpler and more Pythonic for callbacks:

```python
def my_measure(
    known_dimensions: tuple[float | None, float | None],
    available_space: tuple[AvailableSpace, AvailableSpace],
    node_id: NodeId,
    node_context: Any | None,
    style: Style,
) -> Size:
    ...
```

### Step 5: Update Python exports

- `python/waxy/__init__.py` — no changes needed (TaffyTree is already exported)
- `python/waxy/__init__.pyi` — add type signatures for the new methods

### Step 6: Add tests

Test cases:
- `new_leaf_with_context` creates a node with context
- `get_node_context` returns the context
- `set_node_context` updates/clears context
- `compute_layout_with_measure` with a simple fixed-size measure function
- `compute_layout_with_measure` with a text-like measure function that responds to available width
- Measure function receives correct `known_dimensions` when style has explicit size
- Measure function receives correct `node_context` (including `None` for nodes without context)
- Error handling: measure function raises an exception → propagated to caller

## Usage Examples

### Example 1: Fixed-Size Leaf (e.g., an image)

```python
from waxy import TaffyTree, Style, Size, Display, FlexDirection, length

tree = TaffyTree()

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
def measure(known_dimensions, available_space, node_id, context, style):
    kw, kh = known_dimensions
    if kw is not None and kh is not None:
        return Size(kw, kh)

    if context and context["type"] == "image":
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
from waxy import TaffyTree, Style, Size, Display, FlexDirection, length, AvailableSpace

tree = TaffyTree()

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

    if context is None or context["type"] != "text":
        return Size(0, 0)

    text = context["content"]
    words = text.split()
    max_word_len = max(len(w) for w in words) if words else 0
    total_len = sum(len(w) for w in words) + len(words) - 1

    # Determine available inline size
    avail_w = available_space[0]
    if kw is not None:
        inline_size = kw
    elif avail_w.is_definite():
        # Clamp between min (longest word) and max (all on one line)
        inline_size = max(max_word_len * CHAR_WIDTH,
                         min(total_len * CHAR_WIDTH, ???))
        # In practice you'd extract the definite value
        inline_size = total_len * CHAR_WIDTH  # simplified
    else:
        inline_size = total_len * CHAR_WIDTH

    # Count lines by wrapping
    chars_per_line = max(1, int(inline_size / CHAR_WIDTH))
    line_count = 1
    current = 0
    for word in words:
        if current == 0:
            current = len(word)
        elif current + 1 + len(word) > chars_per_line:
            line_count += 1
            current = len(word)
        else:
            current += 1 + len(word)

    return Size(inline_size, line_count * CHAR_HEIGHT)

tree.compute_layout_with_measure(root, measure=measure)
layout = tree.layout(text_node)
print(layout.size)  # Text wrapped within 100px width
```

### Example 3: Multiple Node Types with Shared Measure Function

```python
from waxy import TaffyTree, Style, Size, Display, FlexDirection, length

tree = TaffyTree()

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
    if ctx is None:
        return Size(0, 0)
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
tree = TaffyTree()
node = tree.new_leaf_with_context(Style(), {"text": "Hello"})

# Later, update the text
tree.set_node_context(node, {"text": "Hello, world!"})
# This also marks the node as dirty, so the next compute_layout will re-measure it

# Or remove the context entirely
tree.set_node_context(node, None)
print(tree.get_node_context(node))  # None
```

## Open Questions

1. **`known_dimensions` representation**: Should it be a `tuple[float | None, float | None]` or a custom type like `KnownDimensions(width: float | None, height: float | None)`? A tuple is simpler; a named type is more self-documenting. Recommendation: start with a tuple, we can always add a named wrapper later.

2. **`available_space` representation**: Should it be a `tuple[AvailableSpace, AvailableSpace]` or reuse `Size`-like semantics? Since `AvailableSpace` already exists as a type, a tuple of `(width: AvailableSpace, height: AvailableSpace)` is natural.

3. **Return type flexibility**: Should the measure function be allowed to return a `(float, float)` tuple as well as `Size`? Supporting both adds flexibility. Recommendation: accept either — try to convert as `Size` first, then fall back to unpacking a 2-tuple.

4. **Error propagation**: If the Python measure function raises, the exception should propagate out of `compute_layout_with_measure` as a Python exception. PyO3 supports this naturally.

5. **Should `compute_layout` (without measure) still work?** Yes. The existing `compute_layout` method stays as-is. Leaf nodes without a measure function simply have zero intrinsic size (taffy's default behavior). Users opt in to measure functions by calling `compute_layout_with_measure` instead.
