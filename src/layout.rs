use pyo3::prelude::*;

use crate::geometry::{Point, Rect, Size};

/// The computed layout of a node.
#[pyclass(from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Layout {
    #[pyo3(get)]
    pub order: u32,
    #[pyo3(get)]
    pub location: Point,
    #[pyo3(get)]
    pub size: Size,
    #[pyo3(get)]
    pub content_size: Size,
    #[pyo3(get)]
    pub scrollbar_size: Size,
    #[pyo3(get)]
    pub border: Rect,
    #[pyo3(get)]
    pub padding: Rect,
    #[pyo3(get)]
    pub margin: Rect,
}

#[pymethods]
impl Layout {
    fn __repr__(&self) -> String {
        format!("Layout(location={:?}, size={:?})", self.location, self.size)
    }

    /// Width of the content box (size minus padding and border).
    fn content_box_width(&self) -> f32 {
        self.size.width
            - self.padding.left
            - self.padding.right
            - self.border.left
            - self.border.right
    }

    /// Height of the content box (size minus padding and border).
    fn content_box_height(&self) -> f32 {
        self.size.height
            - self.padding.top
            - self.padding.bottom
            - self.border.top
            - self.border.bottom
    }
}

impl From<&taffy::Layout> for Layout {
    fn from(l: &taffy::Layout) -> Self {
        Self {
            order: l.order,
            location: l.location.into(),
            size: l.size.into(),
            content_size: l.content_size.into(),
            scrollbar_size: l.scrollbar_size.into(),
            border: l.border.into(),
            padding: l.padding.into(),
            margin: l.margin.into(),
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Layout>()?;
    Ok(())
}
