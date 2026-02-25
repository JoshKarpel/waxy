# Plan: Raise Real Exceptions from SlotMap Panics (Issue #28)

**Status: Implemented**

## Background

When a node is removed from a `TaffyTree`, its `NodeId` becomes a stale handle. Taffy stores nodes in three `SlotMap`s (`nodes`, `children`, `parents`). While `SlotMap.get()` safely returns `None` for invalid keys, taffy's methods pervasively use `[]` bracket indexing instead. The `SlotMap` `Index` trait implementation calls `.get()` internally and panics on `None`:

```rust
// From slotmap's Index impl:
fn index(&self, key: K) -> &V {
    match self.get(key) {
        Some(r) => r,
        None => panic!("invalid SlotMap key used"),
    }
}
```

So when waxy calls e.g. `taffy_tree.children(node)` with a removed `NodeId`, taffy internally does `self.children[parent.into()]`, which hits this panic path. PyO3 catches the panic and raises `pyo3_runtime.PanicException` — a subclass of `BaseException`, not `Exception`. This is problematic because:

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
# raises BaseException("invalid SlotMap key used")
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

Taffy's `TaffyTree` struct has three `SlotMap`s:

```rust
nodes: SlotMap<DefaultKey, NodeData>,                    // node style, layout, cache
children: SlotMap<DefaultKey, ChildrenVec<NodeId>>,      // parent → children mapping
parents: SlotMap<DefaultKey, Option<NodeId>>,             // child → parent mapping
node_context_data: SparseSecondaryMap<DefaultKey, NodeContext>,  // optional context
```

When `remove()` is called, it deletes the key from `nodes`, `children`, and `parents`. Any subsequent `[]` access on these slotmaps with the stale key panics. Note that `SparseSecondaryMap` has the same `Index` behavior (panics with `"invalid SparseSecondaryMap key used"`), but taffy accesses `node_context_data` via `.get()` / `.get_mut()`, so it's safe.

### Why taffy uses `[]` instead of `.get()`

This is a known issue upstream. [Issue #519](https://github.com/DioxusLabs/taffy/issues/519) and [PR #520](https://github.com/DioxusLabs/taffy/pull/520) ("Don't return `TaffyResult` when Taffy methods can't fail") document the situation:

- Many taffy methods return `TaffyResult` (a `Result` type) despite never actually returning an `Err` — they panic on invalid keys instead. The `TaffyResult` wrapper is misleading because errors are not recoverable through the `Result` path.
- PR #520 proposes removing `TaffyResult` from these methods to honestly reflect that they either succeed or panic. The PR has been open since July 2023 and remains unmerged.
- Taffy's maintainer (nicoburns) acknowledged the problem: *"Some of these methods are currently using array indexing to access node data (which will panic if the `NodeId` is invalid)"* and suggested *"Possibly we ought to have both panicking and result-returning variants of these methods?"*
- The deeper structural issue is that `NodeId` values can be cloned and persist after the node is removed. Making `NodeId` borrow-based was suggested but rejected because taffy needs cloneable IDs internally during layout computation.

So the `[]` indexing is essentially a conscious trade-off: taffy treats invalid `NodeId` access as a programming error (like indexing out of bounds on a `Vec`) rather than a recoverable error. The `TaffyError` enum has `InvalidParentNode`, `InvalidChildNode`, and `InvalidInputNode` variants, but they're only used for a handful of pre-validation checks (like child index bounds), not for slotmap access.

Downstream consumers like Bevy have also hit this: [bevyengine/bevy#12403](https://github.com/bevyengine/bevy/issues/12403) documents the same `"invalid SlotMap key used"` panic when entities are despawned in the wrong order, fixed by reordering operations ([bevyengine/bevy#13990](https://github.com/bevyengine/bevy/pull/13990)).

Since this is an upstream design choice that's unlikely to change soon (the PR has been open for 2+ years), waxy needs to handle it at our boundary.

The affected waxy methods fall into two categories:

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
| `set_node_context(node, ctx)` | `self.nodes[key]` (sets `has_context` flag) |
| `remove(node)` | `self.parents[key]` (panics on double-remove) |
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
| `get_node_context(node)` | Uses `self.node_context_data.get()` which returns `Option` |
| `clear()` | Clears everything |
| `total_node_count()` | Returns `.len()` |
| `enable_rounding()` | No node access |
| `disable_rounding()` | No node access |
| `with_capacity(n)` | Constructor |

## Design

### New exception: `InvalidNodeId`

Add a new exception using `create_exception!` with `TaffyException` as the base, then use the `__bases__` override pattern (already used for `InvalidPercent`, `InvalidLength`, etc.) to add `KeyError` as a second base class:

```rust
// In errors.rs:
create_exception!(waxy, InvalidNodeId, TaffyException, "Node ID is not valid (node may have been removed).");

// In register():
let taffy_exc_type = py.get_type::<TaffyException>();
let key_error_type = py.get_type::<PyKeyError>();
let bases = pyo3::types::PyTuple::new(py, [taffy_exc_type, key_error_type])?;
let invalid_node_id_type = py.get_type::<InvalidNodeId>();
invalid_node_id_type.setattr("__bases__", &bases)?;
m.add("InvalidNodeId", invalid_node_id_type)?;
```

This gives `isinstance(e, KeyError)` support, matching the issue's suggestion, with no additional complexity — it's the same pattern used for the validation exceptions. Users can catch it with `except InvalidNodeId`, `except KeyError`, `except TaffyException`, or `except Exception`.

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

Every method listed in the "Scope of the Problem" section above needs `catch_unwind`. The safe methods (`new_leaf`, `get_node_context`, `clear`, etc.) do not need wrapping.

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

## Implementation Plan (TDD)

We use red/green TDD: write failing tests first, then implement until they pass.

### Step 1: Add `InvalidNodeId` exception (minimal skeleton)

Create just enough so the tests can import and reference `InvalidNodeId`:

In `src/errors.rs`:
- Add `create_exception!(waxy, InvalidNodeId, TaffyException, "Node ID is not valid.");`
- In `register()`, use the `__bases__` override pattern to set bases to `(TaffyException, KeyError)`, then add to the module

In `python/waxy/__init__.py` — add `InvalidNodeId` to imports and `__all__`.

In `python/waxy/__init__.pyi` — add `InvalidNodeId` exception class.

At this point the exception exists but no method raises it yet — all behavioral tests will be red.

### Step 2: Write tests (RED)

In `tests/test_errors.py`:
- Add `InvalidNodeId` to `EXCEPTION_SUBCLASSES`
- Change the existing `test_invalid_parent_node` test to assert `InvalidNodeId` instead of `BaseException`
- Remove `test_catch_base_exception` (the panic will now be a proper exception)
- Add tests for `InvalidNodeId` on every panicking method: `children`, `child_count`, `parent`, `style`, `set_style`, `layout`, `unrounded_layout`, `mark_dirty`, `dirty`, `set_node_context`, `remove` (double-remove), `add_child`, `insert_child_at_index`, `set_children`, `remove_child`, `remove_child_at_index`, `replace_child_at_index`, `child_at_index`, `new_with_children`, `print_tree`, `compute_layout`
- Add tests verifying `InvalidNodeId` is catchable as `TaffyException`, `KeyError`, and `Exception`

Run tests — confirm they fail (red). The methods still raise `PanicException` / `BaseException`, not `InvalidNodeId`.

### Step 3: Add `catch_panic` helpers

In `src/errors.rs`:
- Add `catch_node_panic(node, f)` for single-node methods
- Add `catch_panic(f)` for multi-node and generic methods

### Step 4: Wrap all panicking `TaffyTree` methods (GREEN)

In `src/tree.rs`, wrap each method listed in the scope section. Methods that currently don't return `PyResult` will be changed to do so. After each batch of methods, run tests to confirm they go green incrementally.

Affected methods (21 total):

**Currently return `PyResult` — add `catch_panic`/`catch_node_panic` wrapper:**
1. `children(parent)` — `catch_node_panic(parent, …)`
2. `set_style(node, style)` — `catch_node_panic(node, …)`
3. `style(node)` — `catch_node_panic(node, …)`
4. `layout(node)` — `catch_node_panic(node, …)`
5. `mark_dirty(node)` — `catch_node_panic(node, …)`
6. `dirty(node)` — `catch_node_panic(node, …)`
7. `set_node_context(node, ctx)` — `catch_node_panic(node, …)`
8. `remove(node)` — `catch_node_panic(node, …)` (panics on double-remove)
9. `add_child(parent, child)` — `catch_panic(…)` (two nodes)
10. `insert_child_at_index(parent, idx, child)` — `catch_panic(…)` (two nodes)
11. `set_children(parent, children)` — `catch_panic(…)` (multiple nodes)
12. `remove_child(parent, child)` — `catch_panic(…)` (two nodes)
13. `remove_child_at_index(parent, idx)` — `catch_node_panic(parent, …)`
14. `replace_child_at_index(parent, idx, new_child)` — `catch_panic(…)` (two nodes)
15. `child_at_index(parent, idx)` — `catch_node_panic(parent, …)`
16. `new_with_children(style, children)` — `catch_panic(…)` (multiple nodes)
17. `compute_layout(node, …)` — `catch_panic(…)` (traverses tree)

**Currently don't return `PyResult` — change return type and add wrapper:**
18. `child_count(parent)` → `PyResult<usize>` — `catch_node_panic(parent, …)`
19. `parent(child)` → `PyResult<Option<NodeId>>` — `catch_node_panic(child, …)`
20. `unrounded_layout(node)` → `PyResult<Layout>` — `catch_node_panic(node, …)`
21. `print_tree(root)` → `PyResult<()>` — `catch_node_panic(root, …)`

**Safe — no wrapping needed:**
- `get_node_context(node)` — uses `SparseSecondaryMap.get()` which returns `Option`, not `[]` indexing

### Step 5: Update `CLAUDE.md`

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

def test_invalid_node_id_is_key_error():
    assert issubclass(waxy.InvalidNodeId, KeyError)

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

1. **Should `InvalidNodeId` inherit from `KeyError`?** Yes. We use the same `__bases__` override pattern already established for validation exceptions (`InvalidPercent`, `InvalidLength`, etc.). This gives users `except KeyError` catchability at no additional complexity.

2. **Should we pre-validate node IDs instead of using `catch_unwind`?** No. Taffy doesn't expose a `contains_node()` method, the slotmap is private, and pre-validation would be subject to TOCTOU issues. `catch_unwind` is the correct approach.

3. **Is `AssertUnwindSafe` safe here?** Yes. The panics occur at slotmap indexing, which is a read operation. No state mutation occurs before the panic, so the tree is not left in an inconsistent state. See the safety argument in the Design section.

4. **What about panics during `compute_layout`?** Wrapped the same way. If a panic occurs during tree traversal (unlikely in normal usage, but possible if the tree is corrupted), it will be caught and converted to `InvalidNodeId`.
