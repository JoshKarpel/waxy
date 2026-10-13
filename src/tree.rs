use std::collections::hash_map::Entry;
use std::fmt::Write;

use pyo3::prelude::*;
use rustc_hash::FxHashMap;
use taffy::prelude as tp;
use taffy::TraversePartialTree;

use crate::errors::{catch_node_panic, catch_panic, taffy_error_to_py, ChildIndexOutOfBounds};
use crate::geometry::{AvailableSize, KnownSize, Point, Size};
use crate::layout::{DetailedGridInfo, Layout};
use crate::node::NodeId;
use crate::style::Style;
use crate::values::NoCalc;

/// A tree of layout nodes.
#[pyclass(module = "waxy")]
pub struct TaffyTree {
    inner: NoCalc<tp::TaffyTree<Py<PyAny>>>,
    /// Mirrors taffy's rounding setting, which taffy doesn't expose.
    is_rounding_enabled: bool,
    /// `compute_layout`'s memo of measure results, empty between calls. Kept here rather than
    /// built per call so its allocation is reused across frames.
    measure_memo: FxHashMap<MeasureKey, taffy::Size<f32>>,
}

#[pymethods]
impl TaffyTree {
    /// Create a new empty layout tree.
    #[new]
    fn new() -> Self {
        Self {
            inner: NoCalc(tp::TaffyTree::new()),
            is_rounding_enabled: true,
            measure_memo: FxHashMap::default(),
        }
    }

    /// Create a new layout tree with pre-allocated capacity.
    #[staticmethod]
    fn with_capacity(capacity: usize) -> Self {
        Self {
            inner: NoCalc(tp::TaffyTree::with_capacity(capacity)),
            is_rounding_enabled: true,
            measure_memo: FxHashMap::default(),
        }
    }

    /// Create a new leaf node with the given style.
    fn new_leaf(&mut self, style: &Style) -> PyResult<NodeId> {
        self.inner
            .new_leaf(style.to_taffy())
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Create a new leaf node with the given style and context.
    fn new_leaf_with_context(&mut self, style: &Style, context: Py<PyAny>) -> PyResult<NodeId> {
        self.inner
            .new_leaf_with_context(style.to_taffy(), context)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Get the context attached to a node, if any.
    fn get_node_context(&self, py: Python<'_>, node: &NodeId) -> Option<Py<PyAny>> {
        self.inner
            .get_node_context(node.inner)
            .map(|ctx| ctx.clone_ref(py))
    }

    /// Set or clear the context attached to a node.
    fn set_node_context(&mut self, node: &NodeId, context: Option<Py<PyAny>>) -> PyResult<()> {
        catch_node_panic(node, || self.inner.set_node_context(node.inner, context))?
            .map_err(taffy_error_to_py)
    }

    /// Create a new node with children.
    fn new_with_children(&mut self, style: &Style, children: Vec<NodeId>) -> PyResult<NodeId> {
        let child_ids: Vec<taffy::NodeId> = children.iter().map(|c| c.inner).collect();
        catch_panic(|| self.inner.new_with_children(style.to_taffy(), &child_ids))?
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Add a child to a parent node.
    fn add_child(&mut self, parent: &NodeId, child: &NodeId) -> PyResult<()> {
        catch_panic(|| self.inner.add_child(parent.inner, child.inner))?.map_err(taffy_error_to_py)
    }

    /// Insert a child at a specific index.
    fn insert_child_at_index(
        &mut self,
        parent: &NodeId,
        child_index: usize,
        child: &NodeId,
    ) -> PyResult<()> {
        catch_panic(|| {
            self.inner
                .insert_child_at_index(parent.inner, child_index, child.inner)
        })?
        .map_err(taffy_error_to_py)
    }

    /// Set the children of a node, replacing any existing children.
    fn set_children(&mut self, parent: &NodeId, children: Vec<NodeId>) -> PyResult<()> {
        let child_ids: Vec<taffy::NodeId> = children.iter().map(|c| c.inner).collect();
        catch_panic(|| self.inner.set_children(parent.inner, &child_ids))?
            .map_err(taffy_error_to_py)
    }

    /// Remove a specific child from a parent.
    fn remove_child(&mut self, parent: &NodeId, child: &NodeId) -> PyResult<NodeId> {
        catch_panic(|| self.inner.remove_child(parent.inner, child.inner))?
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Remove a child at a specific index.
    fn remove_child_at_index(&mut self, parent: &NodeId, child_index: usize) -> PyResult<NodeId> {
        catch_node_panic(parent, || {
            self.inner.remove_child_at_index(parent.inner, child_index)
        })?
        .map(NodeId::from)
        .map_err(taffy_error_to_py)
    }

    /// Detach the children at indices `start` (inclusive) to `end` (exclusive) from a parent.
    fn remove_children_range(&mut self, parent: &NodeId, start: usize, end: usize) -> PyResult<()> {
        let child_count = catch_node_panic(parent, || self.inner.child_count(parent.inner))?;
        // taffy panics on an invalid range rather than returning an error.
        if start > end || end > child_count {
            return Err(ChildIndexOutOfBounds::new_err(format!(
                "Child range {start}..{end} out of bounds (child count: {child_count})"
            )));
        }
        catch_node_panic(parent, || {
            self.inner.remove_children_range(parent.inner, start..end)
        })?
        .map_err(taffy_error_to_py)
    }

    /// Replace the child at a specific index with a new child.
    fn replace_child_at_index(
        &mut self,
        parent: &NodeId,
        child_index: usize,
        new_child: &NodeId,
    ) -> PyResult<NodeId> {
        catch_panic(|| {
            self.inner
                .replace_child_at_index(parent.inner, child_index, new_child.inner)
        })?
        .map(NodeId::from)
        .map_err(taffy_error_to_py)
    }

    /// Get the child at a specific index.
    fn child_at_index(&self, parent: &NodeId, child_index: usize) -> PyResult<NodeId> {
        catch_node_panic(parent, || {
            self.inner.child_at_index(parent.inner, child_index)
        })?
        .map(NodeId::from)
        .map_err(taffy_error_to_py)
    }

    /// Get all children of a node.
    fn children(&self, parent: &NodeId) -> PyResult<Vec<NodeId>> {
        catch_node_panic(parent, || self.inner.children(parent.inner))?
            .map(|ids: Vec<taffy::NodeId>| ids.into_iter().map(NodeId::from).collect())
            .map_err(taffy_error_to_py)
    }

    /// Get the number of children of a node.
    fn child_count(&self, parent: &NodeId) -> PyResult<usize> {
        catch_node_panic(parent, || self.inner.child_count(parent.inner))
    }

    /// Get the parent of a node, if any.
    fn parent(&self, child: &NodeId) -> PyResult<Option<NodeId>> {
        catch_node_panic(child, || self.inner.parent(child.inner).map(NodeId::from))
    }

    /// Get the total number of nodes in the tree.
    fn total_node_count(&self) -> usize {
        self.inner.total_node_count()
    }

    /// Remove a node from the tree.
    fn remove(&mut self, node: &NodeId) -> PyResult<NodeId> {
        catch_node_panic(node, || self.inner.remove(node.inner))?
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Clear all nodes from the tree.
    fn clear(&mut self) {
        self.inner.clear();
    }

    /// Set the style of a node, marking it dirty only if the style changed.
    fn set_style(&mut self, node: &NodeId, style: &Style) -> PyResult<()> {
        // taffy's set_style marks the node dirty unconditionally. Compare `inner` rather than the
        // whole waxy Style, since taffy only ever sees `inner`.
        let current =
            catch_node_panic(node, || self.inner.style(node.inner))?.map_err(taffy_error_to_py)?;
        if *current == *style.inner {
            return Ok(());
        }
        catch_node_panic(node, || self.inner.set_style(node.inner, style.to_taffy()))?
            .map_err(taffy_error_to_py)
    }

    /// Get the style of a node.
    fn style(&self, node: &NodeId) -> PyResult<Style> {
        catch_node_panic(node, || self.inner.style(node.inner))?
            .map(Style::from)
            .map_err(taffy_error_to_py)
    }

    /// Mark a node as dirty (needing re-layout).
    fn mark_dirty(&mut self, node: &NodeId) -> PyResult<()> {
        catch_node_panic(node, || self.inner.mark_dirty(node.inner))?.map_err(taffy_error_to_py)
    }

    /// Check if a node is dirty (needs re-layout).
    fn dirty(&self, node: &NodeId) -> PyResult<bool> {
        catch_node_panic(node, || self.inner.dirty(node.inner))?.map_err(taffy_error_to_py)
    }

    /// Compute the layout of a tree rooted at the given node.
    #[pyo3(signature = (node, available=None, measure=None))]
    fn compute_layout(
        &mut self,
        py: Python<'_>,
        node: &NodeId,
        available: Option<&AvailableSize>,
        measure: Option<Py<PyAny>>,
    ) -> PyResult<()> {
        let avail: taffy::Size<taffy::AvailableSpace> =
            available.map(|a| a.into()).unwrap_or(taffy::Size {
                width: taffy::AvailableSpace::MaxContent,
                height: taffy::AvailableSpace::MaxContent,
            });

        match measure {
            None => catch_panic(|| self.inner.compute_layout(node.inner, avail))?
                .map_err(taffy_error_to_py),
            Some(measure_fn) => {
                // py_err lives outside catch_unwind so it survives a panic unwind.
                let py_err: std::cell::RefCell<Option<PyErr>> = std::cell::RefCell::new(None);
                // taffy's per-node cache evicts inputs it asks for again within the same pass, so
                // answer repeats here instead of calling Python. Cleared when this call returns:
                // a memo that outlived one pass would need invalidating on every change taffy's
                // own dirty tracking already sees.
                let memo = &mut self.measure_memo;
                // Leaves measured as zero because of a Python error. taffy still caches their
                // results and marks them clean, so they're marked dirty again below.
                let mut poisoned: Vec<taffy::NodeId> = Vec::new();

                let result = catch_panic(|| {
                    self.inner.compute_layout_with_measure(
                        node.inner,
                        avail,
                        |inputs, node_id, node_context: Option<&mut Py<PyAny>>, style| {
                            // compute_leaf_layout applies the leaf's own style (padding,
                            // border, min/max size, aspect ratio) around the content size
                            // that the Python measure function reports.
                            taffy::compute_leaf_layout(
                                inputs,
                                style,
                                |_, _| 0.0,
                                |known, available| {
                                    // If we already have a Python error, short-circuit.
                                    if py_err.borrow().is_some() {
                                        poisoned.push(node_id);
                                        return taffy::Size::ZERO;
                                    }

                                    // If both dimensions are already known, return them directly.
                                    if let taffy::Size {
                                        width: Some(w),
                                        height: Some(h),
                                    } = known
                                    {
                                        return taffy::Size {
                                            width: w,
                                            height: h,
                                        };
                                    }

                                    // If no context, return zero — don't bother calling Python.
                                    let Some(context) = node_context else {
                                        return taffy::Size::ZERO;
                                    };

                                    let entry = match memo
                                        .entry(MeasureKey::new(node_id, known, available))
                                    {
                                        Entry::Occupied(entry) => return *entry.get(),
                                        Entry::Vacant(entry) => entry,
                                    };

                                    // Convert to Python types and call the measure function.
                                    let py_known = KnownSize::from(known);
                                    let py_avail = AvailableSize::from(available);

                                    let measured = measure_fn
                                        .call1(py, (py_known, py_avail, context.clone_ref(py)))
                                        .and_then(|result| {
                                            result.extract::<Size>(py).map_err(Into::into)
                                        });

                                    match measured {
                                        Ok(size) => {
                                            let size = taffy::Size::from(&size);
                                            entry.insert(size);
                                            size
                                        }
                                        Err(e) => {
                                            *py_err.borrow_mut() = Some(e);
                                            poisoned.push(node_id);
                                            taffy::Size::ZERO
                                        }
                                    }
                                },
                            )
                        },
                    )
                });
                self.measure_memo.clear();

                // Priority: Python errors first, then panics, then taffy errors.
                if let Some(e) = py_err.into_inner() {
                    // mark_dirty also dirties each ancestor, whose cached layout was built on the
                    // zero sizes, so the next compute_layout measures these leaves again.
                    for leaf in poisoned {
                        self.inner.mark_dirty(leaf).map_err(taffy_error_to_py)?;
                    }
                    return Err(e);
                }
                result?.map_err(taffy_error_to_py)
            }
        }
    }

    /// Get the computed layout of a node.
    fn layout(&self, node: &NodeId) -> PyResult<Layout> {
        catch_node_panic(node, || self.inner.layout(node.inner))?
            .map(Layout::from)
            .map_err(taffy_error_to_py)
    }

    /// Get detailed layout information for a grid container, or `None` for other nodes.
    fn detailed_layout_info(&self, node: &NodeId) -> PyResult<Option<DetailedGridInfo>> {
        catch_node_panic(node, || {
            // taffy only ever writes a node's grid info, never clears it, so a node that stopped
            // being a grid container (or lost its children, making it a leaf) still has the info
            // from its last grid layout.
            let style = self.inner.style(node.inner).map_err(taffy_error_to_py)?;
            if style.display != taffy::Display::Grid || self.inner.child_count(node.inner) == 0 {
                return Ok(None);
            }
            Ok(DetailedGridInfo::from_taffy(
                self.inner.detailed_layout_info(node.inner),
            ))
        })?
    }

    /// Get the unrounded layout of a node.
    fn unrounded_layout(&self, node: &NodeId) -> PyResult<Layout> {
        catch_node_panic(node, || {
            Layout::from(self.inner.unrounded_layout(node.inner))
        })
    }

    /// Enable rounding of layout values.
    fn enable_rounding(&mut self) {
        self.inner.enable_rounding();
        self.is_rounding_enabled = true;
    }

    /// Disable rounding of layout values.
    fn disable_rounding(&mut self) {
        self.inner.disable_rounding();
        self.is_rounding_enabled = false;
    }

    /// Every visible node in the subtree rooted at `root`, in pre-order, with its absolute
    /// position and its layout.
    fn absolute_layouts(&self, root: &NodeId) -> PyResult<Vec<(NodeId, Point, Layout)>> {
        catch_node_panic(root, || self.collect_absolute_layouts(root.inner))?
    }

    /// Print the layout tree for debugging.
    fn print_tree(&mut self, root: &NodeId) -> PyResult<()> {
        catch_node_panic(root, || self.inner.print_tree(root.inner))
    }

    /// An indented dump of the subtree rooted at `root`.
    fn format_tree(&self, py: Python<'_>, root: &NodeId) -> PyResult<String> {
        // taffy's print_tree writes to stdout, which corrupts the screen of a running TUI, so
        // build the string here instead.
        let mut lines = Vec::new();
        catch_node_panic(root, || self.format_node(py, root.inner, 0, &mut lines))??;
        Ok(lines.join("\n"))
    }

    fn __repr__(&self) -> String {
        format!("TaffyTree(nodes={})", self.inner.total_node_count())
    }

    #[classmethod]
    fn __class_getitem__(
        cls: &Bound<'_, pyo3::types::PyType>,
        _item: &Bound<'_, PyAny>,
    ) -> Py<pyo3::types::PyType> {
        cls.clone().unbind()
    }
}

impl TaffyTree {
    fn collect_absolute_layouts(
        &self,
        root: taffy::NodeId,
    ) -> PyResult<Vec<(NodeId, Point, Layout)>> {
        // Sum unrounded locations, rounding each position once at the end: taffy 0.14 rounds
        // each `location` relative to its parent but rounds `size` (and border and padding)
        // against the running absolute offset, so a sum of rounded locations can disagree with
        // the rounded sizes (taffy#834, fixed upstream by taffy#1189 after 0.14.0). Rounding the
        // summed position stays correct after that fix, since fixed rounded locations sum to it.
        // Sum top-down, in the order taffy's round_layout does, so the f32 sums (and so the
        // rounding) match it exactly.
        let mut ancestors = Vec::new();
        let mut ancestor = self.inner.parent(root);
        while let Some(node) = ancestor {
            // A hidden ancestor hides `root` too, the same as a walk from the top would.
            if self.is_hidden(node)? {
                return Ok(Vec::new());
            }
            ancestors.push(node);
            ancestor = self.inner.parent(node);
        }
        let mut origin = taffy::Point::ZERO;
        for node in ancestors.into_iter().rev() {
            let location = self.inner.unrounded_layout(node).location;
            origin = taffy::Point {
                x: origin.x + location.x,
                y: origin.y + location.y,
            };
        }

        let mut layouts = Vec::new();
        let mut pending = vec![(root, origin)];
        while let Some((node, parent_position)) = pending.pop() {
            // taffy lays out a hidden node and its whole subtree as zero-sized boxes at the
            // parent's origin, which would read as real positions, so skip the subtree.
            if self.is_hidden(node)? {
                continue;
            }
            let location = self.inner.unrounded_layout(node).location;
            let position = taffy::Point {
                x: parent_position.x + location.x,
                y: parent_position.y + location.y,
            };
            let reported = if self.is_rounding_enabled {
                taffy::Point {
                    x: round_like_taffy(position.x),
                    y: round_like_taffy(position.y),
                }
            } else {
                position
            };
            layouts.push((
                NodeId::from(node),
                Point::from(reported),
                Layout::from(self.inner.layout(node).map_err(taffy_error_to_py)?),
            ));
            let children = self.inner.children(node).map_err(taffy_error_to_py)?;
            // Pushed in reverse so the first child is popped (and reported) first.
            pending.extend(children.into_iter().rev().map(|child| (child, position)));
        }
        Ok(layouts)
    }

    /// Whether `node` is `display: Nil`, which takes it and its subtree out of the layout.
    fn is_hidden(&self, node: taffy::NodeId) -> PyResult<bool> {
        let style = self.inner.style(node).map_err(taffy_error_to_py)?;
        Ok(style.display == taffy::Display::None)
    }

    /// Append one line per node of the subtree rooted at `node` to `lines`, in pre-order.
    fn format_node(
        &self,
        py: Python<'_>,
        node: taffy::NodeId,
        depth: usize,
        lines: &mut Vec<String>,
    ) -> PyResult<()> {
        let layout = self.inner.layout(node).map_err(taffy_error_to_py)?;
        // Stored styles have no set-field bitmask, so show the fields that differ from taffy's
        // defaults instead.
        let style = self.inner.style(node).map_err(taffy_error_to_py)?;
        let style = Bound::new(py, Style::with_non_default_fields_set(style))?;
        let mut line = "  ".repeat(depth);
        write!(
            line,
            "{} location={} size={} {}",
            NodeId::from(node).__repr__(),
            Point::from(layout.location).__repr__(),
            Size::from(layout.size).__repr__(),
            style.repr()?
        )
        .expect("writing to a String can't fail");
        lines.push(line);
        for child in self.inner.children(node).map_err(taffy_error_to_py)? {
            self.format_node(py, child, depth + 1, lines)?;
        }
        Ok(())
    }
}

/// Round half up, as taffy's (crate-private) `round` does; `f32::round` rounds half away from
/// zero, which disagrees with taffy for negative halves.
fn round_like_taffy(value: f32) -> f32 {
    (value + 0.5).floor()
}

/// A measure call's inputs, with each `f32` keyed by its bits (with `-0.0` normalized to `+0.0`,
/// as `hash_f32` does) so the key can be hashed.
#[derive(PartialEq, Eq, Hash)]
struct MeasureKey {
    node: taffy::NodeId,
    known: [Option<u32>; 2],
    available: [(u8, u32); 2],
}

impl MeasureKey {
    fn new(
        node: taffy::NodeId,
        known: taffy::Size<Option<f32>>,
        available: taffy::Size<taffy::AvailableSpace>,
    ) -> Self {
        let bits = |v: f32| (v + 0.0).to_bits();
        let space = |a: taffy::AvailableSpace| match a {
            taffy::AvailableSpace::Definite(v) => (0, bits(v)),
            taffy::AvailableSpace::MinContent => (1, 0),
            taffy::AvailableSpace::MaxContent => (2, 0),
        };
        Self {
            node,
            known: [known.width.map(bits), known.height.map(bits)],
            available: [space(available.width), space(available.height)],
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TaffyTree>()?;
    Ok(())
}
