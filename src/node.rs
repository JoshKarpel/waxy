use pyo3::prelude::*;

/// A handle to a node in the layout tree.
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct NodeId {
    pub(crate) inner: taffy::NodeId,
}

#[pymethods]
impl NodeId {
    fn __repr__(&self) -> String {
        let val: u64 = self.inner.into();
        format!("NodeId({val})")
    }

    fn __eq__(&self, other: &NodeId) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        let val: u64 = self.inner.into();
        val
    }
}

impl From<taffy::NodeId> for NodeId {
    fn from(id: taffy::NodeId) -> Self {
        Self { inner: id }
    }
}

impl From<&NodeId> for taffy::NodeId {
    fn from(id: &NodeId) -> Self {
        id.inner
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<NodeId>()?;
    Ok(())
}
