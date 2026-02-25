use pyo3::prelude::*;
use taffy::prelude as tp;
use taffy::TraversePartialTree;

use crate::errors::{catch_node_panic, catch_panic, taffy_error_to_py};
use crate::geometry::{AvailableSize, KnownSize};
use crate::layout::Layout;
use crate::node::NodeId;
use crate::style::Style;

/// A tree of layout nodes.
#[pyclass(unsendable, module = "waxy")]
pub struct TaffyTree {
    inner: tp::TaffyTree<Py<PyAny>>,
}

#[pymethods]
impl TaffyTree {
    /// Create a new empty layout tree.
    #[new]
    fn new() -> Self {
        Self {
            inner: tp::TaffyTree::new(),
        }
    }

    /// Create a new layout tree with pre-allocated capacity.
    #[staticmethod]
    fn with_capacity(capacity: usize) -> Self {
        Self {
            inner: tp::TaffyTree::with_capacity(capacity),
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

    /// Set the style of a node.
    fn set_style(&mut self, node: &NodeId, style: &Style) -> PyResult<()> {
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

                let result = catch_panic(|| {
                    self.inner.compute_layout_with_measure(
                        node.inner,
                        avail,
                        |known,
                         available,
                         _node_id,
                         node_context: Option<&mut Py<PyAny>>,
                         _style| {
                            // If we already have a Python error, short-circuit.
                            if py_err.borrow().is_some() {
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

                            // Convert to Python types and call the measure function.
                            let py_known = KnownSize::from(known);
                            let py_avail = AvailableSize::from(available);

                            let call_result =
                                measure_fn.call1(py, (py_known, py_avail, context.clone_ref(py)));

                            match call_result {
                                Err(e) => {
                                    *py_err.borrow_mut() = Some(e);
                                    taffy::Size::ZERO
                                }
                                Ok(result) => match result.extract::<crate::geometry::Size>(py) {
                                    Ok(size) => taffy::Size {
                                        width: size.width,
                                        height: size.height,
                                    },
                                    Err(e) => {
                                        *py_err.borrow_mut() = Some(e.into());
                                        taffy::Size::ZERO
                                    }
                                },
                            }
                        },
                    )
                });

                // Priority: Python errors first, then panics, then taffy errors.
                if let Some(e) = py_err.into_inner() {
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

    /// Get the unrounded layout of a node.
    fn unrounded_layout(&self, node: &NodeId) -> PyResult<Layout> {
        catch_node_panic(node, || {
            Layout::from(self.inner.unrounded_layout(node.inner))
        })
    }

    /// Enable rounding of layout values.
    fn enable_rounding(&mut self) {
        self.inner.enable_rounding();
    }

    /// Disable rounding of layout values.
    fn disable_rounding(&mut self) {
        self.inner.disable_rounding();
    }

    /// Print the layout tree for debugging.
    fn print_tree(&mut self, root: &NodeId) -> PyResult<()> {
        catch_node_panic(root, || self.inner.print_tree(root.inner))
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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TaffyTree>()?;
    Ok(())
}
