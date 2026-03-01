use pyo3::prelude::*;

use crate::geometry::{hash_f32, Point, Rect, Size};

/// The computed layout of a node.
#[pyclass(frozen, from_py_object, module = "waxy")]
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

    fn __eq__(&self, other: &Layout) -> bool {
        self.order == other.order
            && self.location.x == other.location.x
            && self.location.y == other.location.y
            && self.size.width == other.size.width
            && self.size.height == other.size.height
            && self.content_size.width == other.content_size.width
            && self.content_size.height == other.content_size.height
            && self.scrollbar_size.width == other.scrollbar_size.width
            && self.scrollbar_size.height == other.scrollbar_size.height
            && self.border.left == other.border.left
            && self.border.right == other.border.right
            && self.border.top == other.border.top
            && self.border.bottom == other.border.bottom
            && self.padding.left == other.padding.left
            && self.padding.right == other.padding.right
            && self.padding.top == other.padding.top
            && self.padding.bottom == other.padding.bottom
            && self.margin.left == other.margin.left
            && self.margin.right == other.margin.right
            && self.margin.top == other.margin.top
            && self.margin.bottom == other.margin.bottom
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.order.hash(&mut hasher);
        hash_f32(self.location.x, &mut hasher);
        hash_f32(self.location.y, &mut hasher);
        hash_f32(self.size.width, &mut hasher);
        hash_f32(self.size.height, &mut hasher);
        hash_f32(self.content_size.width, &mut hasher);
        hash_f32(self.content_size.height, &mut hasher);
        hash_f32(self.scrollbar_size.width, &mut hasher);
        hash_f32(self.scrollbar_size.height, &mut hasher);
        hash_f32(self.border.left, &mut hasher);
        hash_f32(self.border.right, &mut hasher);
        hash_f32(self.border.top, &mut hasher);
        hash_f32(self.border.bottom, &mut hasher);
        hash_f32(self.padding.left, &mut hasher);
        hash_f32(self.padding.right, &mut hasher);
        hash_f32(self.padding.top, &mut hasher);
        hash_f32(self.padding.bottom, &mut hasher);
        hash_f32(self.margin.left, &mut hasher);
        hash_f32(self.margin.right, &mut hasher);
        hash_f32(self.margin.top, &mut hasher);
        hash_f32(self.margin.bottom, &mut hasher);
        hasher.finish()
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
