use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use taffy::TaffyError;

create_exception!(
    waxy,
    TaffyException,
    PyException,
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

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("TaffyException", m.py().get_type::<TaffyException>())?;
    m.add(
        "ChildIndexOutOfBounds",
        m.py().get_type::<ChildIndexOutOfBounds>(),
    )?;
    m.add("InvalidParentNode", m.py().get_type::<InvalidParentNode>())?;
    m.add("InvalidChildNode", m.py().get_type::<InvalidChildNode>())?;
    m.add("InvalidInputNode", m.py().get_type::<InvalidInputNode>())?;
    Ok(())
}
