use pyo3::prelude::*;

/// A 2D size with width and height.
#[pyclass(module = "waxy")]
#[derive(Clone, Debug)]
pub struct Size {
    #[pyo3(get, set)]
    pub width: f32,
    #[pyo3(get, set)]
    pub height: f32,
}

#[pymethods]
impl Size {
    #[new]
    #[pyo3(signature = (width=0.0, height=0.0))]
    fn new(width: f32, height: f32) -> Self {
        Self { width, height }
    }

    fn __repr__(&self) -> String {
        format!("Size(width={}, height={})", self.width, self.height)
    }

    fn __eq__(&self, other: &Size) -> bool {
        self.width == other.width && self.height == other.height
    }
}

impl From<taffy::Size<f32>> for Size {
    fn from(s: taffy::Size<f32>) -> Self {
        Self {
            width: s.width,
            height: s.height,
        }
    }
}

impl From<&Size> for taffy::Size<f32> {
    fn from(s: &Size) -> Self {
        taffy::Size {
            width: s.width,
            height: s.height,
        }
    }
}

/// A rectangle with left, right, top, bottom edges.
#[pyclass(module = "waxy")]
#[derive(Clone, Debug)]
pub struct Rect {
    #[pyo3(get, set)]
    pub left: f32,
    #[pyo3(get, set)]
    pub right: f32,
    #[pyo3(get, set)]
    pub top: f32,
    #[pyo3(get, set)]
    pub bottom: f32,
}

#[pymethods]
impl Rect {
    #[new]
    #[pyo3(signature = (left=0.0, right=0.0, top=0.0, bottom=0.0))]
    fn new(left: f32, right: f32, top: f32, bottom: f32) -> Self {
        Self {
            left,
            right,
            top,
            bottom,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Rect(left={}, right={}, top={}, bottom={})",
            self.left, self.right, self.top, self.bottom
        )
    }

    fn __eq__(&self, other: &Rect) -> bool {
        self.left == other.left
            && self.right == other.right
            && self.top == other.top
            && self.bottom == other.bottom
    }
}

impl From<taffy::Rect<f32>> for Rect {
    fn from(r: taffy::Rect<f32>) -> Self {
        Self {
            left: r.left,
            right: r.right,
            top: r.top,
            bottom: r.bottom,
        }
    }
}

impl From<&Rect> for taffy::Rect<f32> {
    fn from(r: &Rect) -> Self {
        taffy::Rect {
            left: r.left,
            right: r.right,
            top: r.top,
            bottom: r.bottom,
        }
    }
}

/// A 2D point with x and y coordinates.
#[pyclass(module = "waxy")]
#[derive(Clone, Debug)]
pub struct Point {
    #[pyo3(get, set)]
    pub x: f32,
    #[pyo3(get, set)]
    pub y: f32,
}

#[pymethods]
impl Point {
    #[new]
    #[pyo3(signature = (x=0.0, y=0.0))]
    fn new(x: f32, y: f32) -> Self {
        Self { x, y }
    }

    fn __repr__(&self) -> String {
        format!("Point(x={}, y={})", self.x, self.y)
    }

    fn __eq__(&self, other: &Point) -> bool {
        self.x == other.x && self.y == other.y
    }
}

impl From<taffy::Point<f32>> for Point {
    fn from(p: taffy::Point<f32>) -> Self {
        Self { x: p.x, y: p.y }
    }
}

impl From<&Point> for taffy::Point<f32> {
    fn from(p: &Point) -> Self {
        taffy::Point { x: p.x, y: p.y }
    }
}

/// A line segment with start and end values.
#[pyclass(module = "waxy")]
#[derive(Clone, Debug)]
pub struct Line {
    #[pyo3(get, set)]
    pub start: f32,
    #[pyo3(get, set)]
    pub end: f32,
}

#[pymethods]
impl Line {
    #[new]
    #[pyo3(signature = (start=0.0, end=0.0))]
    fn new(start: f32, end: f32) -> Self {
        Self { start, end }
    }

    fn __repr__(&self) -> String {
        format!("Line(start={}, end={})", self.start, self.end)
    }

    fn __eq__(&self, other: &Line) -> bool {
        self.start == other.start && self.end == other.end
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Size>()?;
    m.add_class::<Rect>()?;
    m.add_class::<Point>()?;
    m.add_class::<Line>()?;
    Ok(())
}
