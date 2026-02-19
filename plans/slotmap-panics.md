# Plan: Raise Real Exceptions from SlotMap Panics (Issue #28)

**Status: Planned**

## Background

When a node is removed from a `TaffyTree`, its `NodeId` becomes a stale handle. Taffy stores nodes in a `SlotMap`, and accessing a removed node panics with `"invalid SlotMap key used"`. PyO3 catches this panic and raises `pyo3_runtime.PanicException` — a subclass of `BaseException`, not `Exception`. This is problematic because:

1. **`except Exception` doesn't catch it.** Users writing normal error-handling code will miss it entirely. The panic propagates to the top level and kills the program.
2. **It's not importable.** `pyo3_runtime.PanicException` can't be imported from Python, so you can't catch it by type — only by `BaseException` with a message match, which is fragile.
3. **The error message is opaque.** `"invalid SlotMap key used"` says nothing about nodes, trees, or waxy.

The issue requests that accessing a removed node raise a proper Python exception — ideally one that inherits from both a waxy exception class and `KeyError`.

### Current Behavior

```python
tree = TaffyTree()
node = tree.new_leaf(Style())
tree.remove(node)

tree.children(node)
# raises BaseException("called `SlotMap::get` on an invalid key")
# — can only be caught with `except BaseException`
```

### Desired Behavior

```python
tree.children(node)
# raises InvalidNodeId("...")
# — catchable with `except InvalidNodeId`, `except KeyError`,
#   `except TaffyException`, or `except Exception`
```

## Scope of the Problem

Taffy's `TaffyTree` internally uses three `SlotMap`s: `nodes`, `children`, and `parents`. Many methods index directly into these maps without bounds checking. The affected waxy methods fall into two categories:

### Methods that return `Result<T, TaffyError>` but still panic on invalid keys

These methods go through `taffy_error_to_py` in waxy, but the slotmap panic happens *before* taffy can return an error:

| Waxy method | Taffy access pattern |
|---|---|
| `children(parent)` | `self.children[parent.into()]` |
| `set_style(node, style)` | `self.nodes[node.into()]` |
| `style(node)` | `self.nodes[node.into()]` |
| `layout(node)` | `self.nodes[node.into()]` |
| `mark_dirty(node)` | `self.nodes[node_key]` (recursive) |
| `dirty(node)` | `self.nodes[node.into()]` |
| `set_node_context(node, ctx)` | `self.nodes[key]` |
| `add_child(parent, child)` | `self.parents[child_key]`, `self.children[parent_key]` |
| `insert_child_at_index(…)` | `self.children[parent_key]` |
| `set_children(parent, children)` | `self.children[parent_key]` |
| `remove_child(parent, child)` | `self.children[parent.into()]` |
| `remove_child_at_index(…)` | `self.children[parent_key]` |
| `replace_child_at_index(…)` | `self.children[parent_key]` |
| `child_at_index(parent, idx)` | `self.children[parent_key]` |
| `new_with_children(…)` | `self.parents[(*child).into()]` for each child |
| `compute_layout(node, …)` | Internal access during traversal |

### Methods that don't return `Result` at all (panic is the only failure mode)

| Waxy method | Return type | Taffy access pattern |
|---|---|---|
| `child_count(parent)` | `usize` | `self.children[parent.into()]` |
| `parent(child)` | `Option<NodeId>` | `self.parents[child.into()]` |
| `unrounded_layout(node)` | `Layout` | `self.nodes[node.into()]` |
| `print_tree(root)` | `()` | `self.nodes[node.into()]` via `PrintTree` |

### Methods that are safe (cannot panic on invalid keys)

| Waxy method | Why safe |
|---|---|
| `new_leaf(style)` | Creates a new node, never indexes |
| `new_leaf_with_context(…)` | Creates a new node |
| `remove(node)` | Uses `.get()` (returns `Option`), never direct indexing |
| `clear()` | Clears everything |
| `total_node_count()` | Returns `.len()` |
| `enable_rounding()` | No node access |
| `disable_rounding()` | No node access |
| `with_capacity(n)` | Constructor |

## Design

### New exception: `InvalidNodeId`

Add a new exception that inherits from both `TaffyException` and `KeyError`:

```rust
create_exception!(waxy, InvalidNodeId, TaffyException, "Node ID is not valid (node may have been removed).");
```

For the `KeyError` inheritance, we need a Python-side class that uses multiple inheritance. PyO3's `create_exception!` only supports a single base class. There are two approaches:

#### Option A: Pure `TaffyException` subclass (no `KeyError`)

```rust
create_exception!(waxy, InvalidNodeId, TaffyException, "Node ID is not valid.");
```

Simple, consistent with the existing exception hierarchy. Users catch it with `except InvalidNodeId` or `except TaffyException` or `except Exception`.

#### Option B: Multiple inheritance via Python-defined class

Define `InvalidNodeId` in Python (`__init__.py`) as:

```python
class InvalidNodeId(TaffyException, KeyError):
    """Node ID is not valid (node may have been removed)."""
```

Then import it on the Rust side, or have the Rust code look it up from the module and raise it. This gives `isinstance(e, KeyError)` support, matching the issue's suggestion.

**Recommendation: Option A.** Multiple inheritance with `KeyError` adds complexity for marginal benefit. The semantics don't perfectly match `KeyError` — the user didn't pass a "key" they constructed, they passed a `NodeId` handle that became stale. `InvalidNodeId` as a `TaffyException` subclass is clear, consistent, and catchable with `except Exception`. If `KeyError` inheritance is desired later, it can be added.

### Strategy: `catch_unwind` wrapper

Since we cannot modify taffy's source code and the panics originate deep inside taffy's slotmap indexing, the only reliable approach is to catch the panic at the waxy boundary and convert it to a Python exception.

Wrap each `TaffyTree` method that can panic in `std::panic::catch_unwind`, converting panics to `InvalidNodeId`:

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};

fn catch_panic<F, T>(f: F) -> PyResult<T>
where
    F: FnOnce() -> T,
{
    catch_unwind(AssertUnwindSafe(f)).map_err(|panic| {
        let msg = if let Some(s) = panic.downcast_ref::<&str>() {
            s.to_string()
        } else if let Some(s) = panic.downcast_ref::<String>() {
            s.clone()
        } else {
            "unknown panic".to_string()
        };
        InvalidNodeId::new_err(msg)
    })
}
```

The `AssertUnwindSafe` wrapper is needed because `TaffyTree` contains `Py<PyAny>` which is not `UnwindSafe`. This is safe in our case because we're at the FFI boundary and the `TaffyTree` won't be in an inconsistent state after a slotmap index panic (the panic occurs before any mutation).

#### Why `catch_unwind` instead of pre-validation?

1. **No validation API.** Taffy does not expose a method to check whether a `NodeId` is valid (e.g., `contains_node(id) -> bool`). The slotmap is private.
2. **TOCTOU races.** Even if we could validate, the check would be non-atomic with the access.
3. **Comprehensive.** `catch_unwind` catches all panics regardless of which internal slotmap triggers them, including panics from child/parent slotmaps and panics during `compute_layout` traversal.
4. **Zero overhead on success.** `catch_unwind` is essentially free when no panic occurs — it only pays cost on the error path.

#### `AssertUnwindSafe` safety argument

`TaffyTree` wraps `taffy::TaffyTree<Py<PyAny>>`. Neither `Py<PyAny>` nor `taffy::TaffyTree` implement `UnwindSafe`. However:

- **SlotMap index panics are non-mutating.** The panic occurs at the `[]` indexing operation, which reads from the slotmap. No state is modified before the panic. The tree remains in its prior valid state.
- **We're at the FFI boundary.** If the panic were to corrupt state, the same corruption would happen today (PyO3 already catches the panic and converts it to `PanicException`). We're just changing the exception type.
- **Mutating methods.** For methods like `add_child`, `set_style`, etc., the panic occurs when accessing the slotmap *before* any mutation happens. The tree is not left in a half-modified state.

### Which methods need wrapping

Every method listed in the "Scope of the Problem" section above needs `catch_unwind`. The safe methods (`new_leaf`, `remove`, `clear`, etc.) do not need wrapping.

#### Methods returning `PyResult` (already have `.map_err(taffy_error_to_py)`)

These need `catch_unwind` added around the inner taffy call. The pattern:

```rust
// Before:
fn children(&self, parent: &NodeId) -> PyResult<Vec<NodeId>> {
    self.inner
        .children(parent.inner)
        .map(|ids| ids.into_iter().map(NodeId::from).collect())
        .map_err(taffy_error_to_py)
}

// After:
fn children(&self, parent: &NodeId) -> PyResult<Vec<NodeId>> {
    catch_panic(|| self.inner.children(parent.inner))?
        .map(|ids| ids.into_iter().map(NodeId::from).collect())
        .map_err(taffy_error_to_py)
}
```

`catch_panic` returns `PyResult<Result<T, TaffyError>>`. The `?` unwraps the panic case, then `.map_err(taffy_error_to_py)` handles normal taffy errors.

#### Methods NOT returning `PyResult` (need signature change)

These methods currently can't fail from Python's perspective. They need to be changed to return `PyResult<T>`:

```rust
// Before:
fn child_count(&self, parent: &NodeId) -> usize {
    self.inner.child_count(parent.inner)
}

// After:
fn child_count(&self, parent: &NodeId) -> PyResult<usize> {
    catch_panic(|| self.inner.child_count(parent.inner))
}
```

**Python API impact:** The return types don't change from the user's perspective — PyO3 automatically unwraps `PyResult`, and the only visible difference is that these methods can now raise `InvalidNodeId` instead of crashing. The `.pyi` stubs don't need to change their return types since PyO3 handles the `PyResult` unwrapping transparently.

#### `compute_layout` — special case

`compute_layout` is more complex because it runs a closure. The entire `compute_layout_with_measure` call needs to be wrapped in `catch_unwind`:

```rust
// The catch_unwind wraps the entire compute_layout/compute_layout_with_measure call
catch_panic(|| {
    self.inner.compute_layout(node.inner, avail)
})?.map_err(taffy_error_to_py)
```

For the `measure` variant, the closure captures `&mut py_err` which adds complexity. The simplest approach is to wrap the entire `compute_layout_with_measure` call in `catch_unwind`. If a panic occurs during traversal (because an internally-referenced node is somehow invalid), it will be caught.

### Error message

The exception message should be user-friendly and explain what happened:

```
InvalidNodeId: node NodeId(42) is not present in the tree (was it removed?)
```

To produce this message, we can format the `NodeId` in the catch_panic call site where we have access to the node parameter. A helper that takes the node being accessed:

```rust
fn catch_node_panic<F, T>(node: &NodeId, f: F) -> PyResult<T>
where
    F: FnOnce() -> T,
{
    catch_unwind(AssertUnwindSafe(f)).map_err(|_| {
        InvalidNodeId::new_err(format!(
            "node {} is not present in the tree (was it removed?)",
            node.__repr__()
        ))
    })
}
```

For methods that take multiple node arguments (e.g., `add_child(parent, child)`), we can't know which one caused the panic. In that case, we use a generic message:

```rust
fn catch_panic_generic<F, T>(f: F) -> PyResult<T>
where
    F: FnOnce() -> T,
{
    catch_unwind(AssertUnwindSafe(f)).map_err(|_| {
        InvalidNodeId::new_err(
            "a node ID is not present in the tree (was it removed?)"
        )
    })
}
```

## Implementation Plan

### Step 1: Add `InvalidNodeId` exception

In `src/errors.rs`:
- Add `create_exception!(waxy, InvalidNodeId, TaffyException, "Node ID is not valid.");`
- Register it in `register()`

### Step 2: Add `catch_panic` helpers

In `src/errors.rs` (or a new `src/panic.rs` if preferred, but `errors.rs` is the natural home):
- Add `catch_node_panic(node, f)` for single-node methods
- Add `catch_panic(f)` for multi-node and generic methods

### Step 3: Wrap all panicking `TaffyTree` methods

In `src/tree.rs`, wrap each method listed in the scope section. Methods that currently don't return `PyResult` will be changed to do so.

Affected methods (21 total):

**Currently return `PyResult` — add `catch_panic`/`catch_node_panic` wrapper:**
1. `children(parent)` — `catch_node_panic(parent, …)`
2. `set_style(node, style)` — `catch_node_panic(node, …)`
3. `style(node)` — `catch_node_panic(node, …)`
4. `layout(node)` — `catch_node_panic(node, …)`
5. `mark_dirty(node)` — `catch_node_panic(node, …)`
6. `dirty(node)` — `catch_node_panic(node, …)`
7. `set_node_context(node, ctx)` — `catch_node_panic(node, …)`
8. `add_child(parent, child)` — `catch_panic(…)` (two nodes)
9. `insert_child_at_index(parent, idx, child)` — `catch_panic(…)` (two nodes)
10. `set_children(parent, children)` — `catch_panic(…)` (multiple nodes)
11. `remove_child(parent, child)` — `catch_panic(…)` (two nodes)
12. `remove_child_at_index(parent, idx)` — `catch_node_panic(parent, …)`
13. `replace_child_at_index(parent, idx, new_child)` — `catch_panic(…)` (two nodes)
14. `child_at_index(parent, idx)` — `catch_node_panic(parent, …)`
15. `new_with_children(style, children)` — `catch_panic(…)` (multiple nodes)
16. `compute_layout(node, …)` — `catch_panic(…)` (traverses tree)

**Currently don't return `PyResult` — change return type and add wrapper:**
17. `child_count(parent)` → `PyResult<usize>` — `catch_node_panic(parent, …)`
18. `parent(child)` → `PyResult<Option<NodeId>>` — `catch_node_panic(child, …)`
19. `unrounded_layout(node)` → `PyResult<Layout>` — `catch_node_panic(node, …)`
20. `print_tree(root)` → `PyResult<()>` — `catch_node_panic(root, …)`
21. `get_node_context(node)` → `PyResult<Option<…>>` — `catch_node_panic(node, …)`

### Step 4: Update Python exports

- `python/waxy/__init__.py` — add `InvalidNodeId` to imports and `__all__`
- `python/waxy/__init__.pyi` — add `InvalidNodeId` exception class

### Step 5: Update tests

In `tests/test_errors.py`:
- Add `InvalidNodeId` to `EXCEPTION_SUBCLASSES`
- Change the existing `test_invalid_parent_node` test to assert `InvalidNodeId` instead of `BaseException`
- Remove `test_catch_base_exception` or update it (since the panic is now a proper exception)
- Add tests for `InvalidNodeId` on various methods: `children`, `child_count`, `parent`, `style`, `layout`, `set_style`, etc.
- Verify `InvalidNodeId` is catchable as `TaffyException` and `Exception`

### Step 6: Update `CLAUDE.md`

Update the "Removed node access" bullet point to reflect the new behavior:
- Old: "**Removed node access** causes a Rust panic (slotmap behavior), not a `TaffyError`."
- New: "**Removed node access** raises `InvalidNodeId` (a `TaffyException` subclass). This is implemented via `catch_unwind` around taffy calls, since taffy panics on invalid slotmap keys."

## Testing Strategy

```python
def test_invalid_node_id_on_removed_node():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.children(node)

def test_invalid_node_id_is_taffy_exception():
    assert issubclass(waxy.InvalidNodeId, waxy.TaffyException)

def test_invalid_node_id_is_exception():
    # Verify it's catchable with `except Exception`
    assert issubclass(waxy.InvalidNodeId, Exception)

def test_invalid_node_id_child_count():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.child_count(node)

def test_invalid_node_id_parent():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.parent(node)

def test_invalid_node_id_layout():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.layout(node)

def test_invalid_node_id_style():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.style(node)

def test_invalid_node_id_set_style():
    tree = TaffyTree()
    node = tree.new_leaf(Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.set_style(node, Style())
```

## Resolved Questions

1. **Should `InvalidNodeId` inherit from `KeyError`?** No. While the issue suggests it, `KeyError` semantics don't match well — the user didn't construct or look up a key, they used a handle that became stale. `TaffyException` subclass is consistent with the existing hierarchy and sufficient for all error-handling patterns. This can be reconsidered later if needed.

2. **Should we pre-validate node IDs instead of using `catch_unwind`?** No. Taffy doesn't expose a `contains_node()` method, the slotmap is private, and pre-validation would be subject to TOCTOU issues. `catch_unwind` is the correct approach.

3. **Is `AssertUnwindSafe` safe here?** Yes. The panics occur at slotmap indexing, which is a read operation. No state mutation occurs before the panic, so the tree is not left in an inconsistent state. See the safety argument in the Design section.

4. **What about panics during `compute_layout`?** Wrapped the same way. If a panic occurs during tree traversal (unlikely in normal usage, but possible if the tree is corrupted), it will be caught and converted to `InvalidNodeId`.
