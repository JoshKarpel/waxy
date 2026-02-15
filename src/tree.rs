use pyo3::prelude::*;
use taffy::prelude as tp;
use taffy::TraversePartialTree;

use crate::enums::AvailableSpace;
use crate::errors::taffy_error_to_py;
use crate::layout::Layout;
use crate::node::NodeId;
use crate::style::Style;

/// A tree of layout nodes.
#[pyclass(unsendable)]
pub struct TaffyTree {
    inner: tp::TaffyTree,
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

    /// Create a new node with children.
    fn new_with_children(&mut self, style: &Style, children: Vec<NodeId>) -> PyResult<NodeId> {
        let child_ids: Vec<taffy::NodeId> = children.iter().map(|c| c.inner).collect();
        self.inner
            .new_with_children(style.to_taffy(), &child_ids)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Add a child to a parent node.
    fn add_child(&mut self, parent: &NodeId, child: &NodeId) -> PyResult<()> {
        self.inner
            .add_child(parent.inner, child.inner)
            .map_err(taffy_error_to_py)
    }

    /// Insert a child at a specific index.
    fn insert_child_at_index(
        &mut self,
        parent: &NodeId,
        child_index: usize,
        child: &NodeId,
    ) -> PyResult<()> {
        self.inner
            .insert_child_at_index(parent.inner, child_index, child.inner)
            .map_err(taffy_error_to_py)
    }

    /// Set the children of a node, replacing any existing children.
    fn set_children(&mut self, parent: &NodeId, children: Vec<NodeId>) -> PyResult<()> {
        let child_ids: Vec<taffy::NodeId> = children.iter().map(|c| c.inner).collect();
        self.inner
            .set_children(parent.inner, &child_ids)
            .map_err(taffy_error_to_py)
    }

    /// Remove a specific child from a parent.
    fn remove_child(&mut self, parent: &NodeId, child: &NodeId) -> PyResult<NodeId> {
        self.inner
            .remove_child(parent.inner, child.inner)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Remove a child at a specific index.
    fn remove_child_at_index(&mut self, parent: &NodeId, child_index: usize) -> PyResult<NodeId> {
        self.inner
            .remove_child_at_index(parent.inner, child_index)
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
        self.inner
            .replace_child_at_index(parent.inner, child_index, new_child.inner)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Get the child at a specific index.
    fn child_at_index(&self, parent: &NodeId, child_index: usize) -> PyResult<NodeId> {
        self.inner
            .child_at_index(parent.inner, child_index)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Get all children of a node.
    fn children(&self, parent: &NodeId) -> PyResult<Vec<NodeId>> {
        self.inner
            .children(parent.inner)
            .map(|ids| ids.into_iter().map(NodeId::from).collect())
            .map_err(taffy_error_to_py)
    }

    /// Get the number of children of a node.
    fn child_count(&self, parent: &NodeId) -> usize {
        self.inner.child_count(parent.inner)
    }

    /// Get the parent of a node, if any.
    fn parent(&self, child: &NodeId) -> Option<NodeId> {
        self.inner.parent(child.inner).map(NodeId::from)
    }

    /// Get the total number of nodes in the tree.
    fn total_node_count(&self) -> usize {
        self.inner.total_node_count()
    }

    /// Remove a node from the tree.
    fn remove(&mut self, node: &NodeId) -> PyResult<NodeId> {
        self.inner
            .remove(node.inner)
            .map(NodeId::from)
            .map_err(taffy_error_to_py)
    }

    /// Clear all nodes from the tree.
    fn clear(&mut self) {
        self.inner.clear();
    }

    /// Set the style of a node.
    fn set_style(&mut self, node: &NodeId, style: &Style) -> PyResult<()> {
        self.inner
            .set_style(node.inner, style.to_taffy())
            .map_err(taffy_error_to_py)
    }

    /// Get the style of a node.
    fn style(&self, node: &NodeId) -> PyResult<Style> {
        self.inner
            .style(node.inner)
            .map(Style::from)
            .map_err(taffy_error_to_py)
    }

    /// Mark a node as dirty (needing re-layout).
    fn mark_dirty(&mut self, node: &NodeId) -> PyResult<()> {
        self.inner.mark_dirty(node.inner).map_err(taffy_error_to_py)
    }

    /// Check if a node is dirty (needs re-layout).
    fn dirty(&self, node: &NodeId) -> PyResult<bool> {
        self.inner.dirty(node.inner).map_err(taffy_error_to_py)
    }

    /// Compute the layout of a tree rooted at the given node.
    #[pyo3(signature = (node, available_width=None, available_height=None))]
    fn compute_layout(
        &mut self,
        node: &NodeId,
        available_width: Option<&AvailableSpace>,
        available_height: Option<&AvailableSpace>,
    ) -> PyResult<()> {
        let width: taffy::AvailableSpace = available_width
            .map(|a| a.into())
            .unwrap_or(taffy::AvailableSpace::MaxContent);
        let height: taffy::AvailableSpace = available_height
            .map(|a| a.into())
            .unwrap_or(taffy::AvailableSpace::MaxContent);

        self.inner
            .compute_layout(node.inner, taffy::Size { width, height })
            .map_err(taffy_error_to_py)
    }

    /// Get the computed layout of a node.
    fn layout(&self, node: &NodeId) -> PyResult<Layout> {
        self.inner
            .layout(node.inner)
            .map(Layout::from)
            .map_err(taffy_error_to_py)
    }

    /// Get the unrounded layout of a node.
    fn unrounded_layout(&self, node: &NodeId) -> Layout {
        Layout::from(self.inner.unrounded_layout(node.inner))
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
    fn print_tree(&mut self, root: &NodeId) {
        self.inner.print_tree(root.inner);
    }

    fn __repr__(&self) -> String {
        format!("TaffyTree(nodes={})", self.inner.total_node_count())
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TaffyTree>()?;
    Ok(())
}
