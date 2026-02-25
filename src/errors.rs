use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyKeyError, PyValueError};
use pyo3::prelude::*;
use taffy::TaffyError;

create_exception!(
    waxy,
    WaxyException,
    PyException,
    "Base exception for all waxy errors."
);
create_exception!(
    waxy,
    TaffyException,
    WaxyException,
    "Base exception for all taffy errors."
);
create_exception!(
    waxy,
    ChildIndexOutOfBounds,
    TaffyException,
    "Child index is out of bounds."
);
create_exception!(
    waxy,
    InvalidParentNode,
    TaffyException,
    "Parent node is invalid."
);
create_exception!(
    waxy,
    InvalidChildNode,
    TaffyException,
    "Child node is invalid."
);
create_exception!(
    waxy,
    InvalidInputNode,
    TaffyException,
    "Input node is invalid."
);
create_exception!(
    waxy,
    InvalidNodeId,
    TaffyException,
    "Node ID is not valid (node may have been removed)."
);
// InvalidPercent, InvalidLength, InvalidGridLine, InvalidGridSpan are defined as subclasses
// of WaxyException initially; we set __bases__ to (WaxyException, ValueError) in register()
// to achieve multi-inheritance.
create_exception!(
    waxy,
    InvalidPercent,
    WaxyException,
    "Raised when Percent(value) is called with value outside [0.0, 1.0]."
);
create_exception!(
    waxy,
    InvalidLength,
    WaxyException,
    "Raised when Length(value) is called with a NaN value."
);
create_exception!(
    waxy,
    InvalidGridLine,
    WaxyException,
    "Raised when GridLine(index) is called with index 0 (grid lines are 1-based)."
);
create_exception!(
    waxy,
    InvalidGridSpan,
    WaxyException,
    "Raised when GridSpan(count) is called with count 0 (must span at least 1 track)."
);

pub fn taffy_error_to_py(err: TaffyError) -> PyErr {
    match err {
        TaffyError::ChildIndexOutOfBounds {
            parent: _,
            child_index,
            child_count,
        } => ChildIndexOutOfBounds::new_err(format!(
            "Child index {child_index} out of bounds (child count: {child_count})"
        )),
        TaffyError::InvalidParentNode(node) => {
            InvalidParentNode::new_err(format!("Invalid parent node: {node:?}"))
        }
        TaffyError::InvalidChildNode(node) => {
            InvalidChildNode::new_err(format!("Invalid child node: {node:?}"))
        }
        TaffyError::InvalidInputNode(node) => {
            InvalidInputNode::new_err(format!("Invalid input node: {node:?}"))
        }
    }
}

/// Extract a message from a panic payload.
fn panic_message(panic: &Box<dyn std::any::Any + Send>) -> String {
    if let Some(s) = panic.downcast_ref::<&str>() {
        s.to_string()
    } else if let Some(s) = panic.downcast_ref::<String>() {
        s.clone()
    } else {
        "unknown panic".to_string()
    }
}

/// Check if a panic payload is from a slotmap invalid key access.
fn is_slotmap_panic(panic: &Box<dyn std::any::Any + Send>) -> bool {
    let msg = panic_message(panic);
    msg.contains("invalid SlotMap key used") || msg.contains("invalid SparseSecondaryMap key used")
}

/// Convert a panic payload to an appropriate Python exception.
/// Slotmap key panics become `InvalidNodeId`; other panics become `TaffyException`.
fn panic_to_py_err(panic: Box<dyn std::any::Any + Send>, node_msg: &str) -> PyErr {
    if is_slotmap_panic(&panic) {
        InvalidNodeId::new_err(node_msg.to_string())
    } else {
        let msg = panic_message(&panic);
        TaffyException::new_err(format!("unexpected taffy panic: {msg}"))
    }
}

/// Catch a panic from a taffy call on a single node and convert it to `InvalidNodeId`.
pub fn catch_node_panic<F, T>(node: &crate::node::NodeId, f: F) -> PyResult<T>
where
    F: FnOnce() -> T,
{
    let node_val: u64 = node.inner.into();
    std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).map_err(|panic| {
        panic_to_py_err(
            panic,
            &format!("node NodeId({node_val}) is not present in the tree (was it removed?)"),
        )
    })
}

/// Catch a panic from a taffy call involving multiple nodes and convert it to `InvalidNodeId`.
pub fn catch_panic<F, T>(f: F) -> PyResult<T>
where
    F: FnOnce() -> T,
{
    std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).map_err(|panic| {
        panic_to_py_err(
            panic,
            "a node ID is not present in the tree (was it removed?)",
        )
    })
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = m.py();

    m.add("WaxyException", py.get_type::<WaxyException>())?;
    m.add("TaffyException", py.get_type::<TaffyException>())?;
    m.add(
        "ChildIndexOutOfBounds",
        py.get_type::<ChildIndexOutOfBounds>(),
    )?;
    m.add("InvalidParentNode", py.get_type::<InvalidParentNode>())?;
    m.add("InvalidChildNode", py.get_type::<InvalidChildNode>())?;
    m.add("InvalidInputNode", py.get_type::<InvalidInputNode>())?;

    // Set __bases__ = (TaffyException, KeyError) for InvalidNodeId.
    let taffy_exc_type = py.get_type::<TaffyException>();
    let key_error_type = py.get_type::<PyKeyError>();
    let node_id_bases =
        pyo3::types::PyTuple::new(py, [taffy_exc_type.clone(), key_error_type.clone()])?;
    let invalid_node_id_type = py.get_type::<InvalidNodeId>();
    invalid_node_id_type.setattr("__bases__", &node_id_bases)?;
    m.add("InvalidNodeId", invalid_node_id_type)?;

    // Set __bases__ = (WaxyException, ValueError) for multi-inheritance on validation errors.
    let waxy_exc_type = py.get_type::<WaxyException>();
    let value_error_type = py.get_type::<PyValueError>();
    let bases = pyo3::types::PyTuple::new(py, [waxy_exc_type.clone(), value_error_type.clone()])?;

    let invalid_percent_type = py.get_type::<InvalidPercent>();
    invalid_percent_type.setattr("__bases__", &bases)?;
    m.add("InvalidPercent", invalid_percent_type)?;

    let invalid_length_type = py.get_type::<InvalidLength>();
    invalid_length_type.setattr("__bases__", &bases)?;
    m.add("InvalidLength", invalid_length_type)?;

    let invalid_grid_line_type = py.get_type::<InvalidGridLine>();
    invalid_grid_line_type.setattr("__bases__", &bases)?;
    m.add("InvalidGridLine", invalid_grid_line_type)?;

    let invalid_grid_span_type = py.get_type::<InvalidGridSpan>();
    invalid_grid_span_type.setattr("__bases__", &bases)?;
    m.add("InvalidGridSpan", invalid_grid_span_type)?;

    Ok(())
}
