use pyo3::prelude::*;

/// A 2D size with width and height.
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Size {
    #[pyo3(get)]
    pub width: f32,
    #[pyo3(get)]
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

    /// The area (width * height).
    #[getter]
    fn area(&self) -> f32 {
        self.width * self.height
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
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Rect {
    #[pyo3(get)]
    pub left: f32,
    #[pyo3(get)]
    pub right: f32,
    #[pyo3(get)]
    pub top: f32,
    #[pyo3(get)]
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

    /// The width of the rectangle (right - left).
    #[getter]
    fn width(&self) -> f32 {
        self.right - self.left
    }

    /// The height of the rectangle (bottom - top).
    #[getter]
    fn height(&self) -> f32 {
        self.bottom - self.top
    }

    /// The size of the rectangle as a Size.
    #[getter]
    fn size(&self) -> Size {
        Size {
            width: self.right - self.left,
            height: self.bottom - self.top,
        }
    }

    /// Check if a point is inside this rectangle.
    fn contains(&self, point: &Point) -> bool {
        point.x >= self.left
            && point.x <= self.right
            && point.y >= self.top
            && point.y <= self.bottom
    }

    /// The top-left corner point.
    #[getter]
    fn top_left(&self) -> Point {
        Point {
            x: self.left,
            y: self.top,
        }
    }

    /// The top-right corner point.
    #[getter]
    fn top_right(&self) -> Point {
        Point {
            x: self.right,
            y: self.top,
        }
    }

    /// The bottom-right corner point.
    #[getter]
    fn bottom_right(&self) -> Point {
        Point {
            x: self.right,
            y: self.bottom,
        }
    }

    /// The bottom-left corner point.
    #[getter]
    fn bottom_left(&self) -> Point {
        Point {
            x: self.left,
            y: self.bottom,
        }
    }

    /// Return the four corner points (top-left, top-right, bottom-right, bottom-left).
    fn corners(&self) -> (Point, Point, Point, Point) {
        (
            self.top_left(),
            self.top_right(),
            self.bottom_right(),
            self.bottom_left(),
        )
    }

    /// Iterate over integer pixel locations along the top edge.
    fn top_edge(&self) -> PixelIter {
        let y = self.top.ceil() as i32;
        PixelIter {
            x_start: self.left.ceil() as i32,
            x_end: self.right.floor() as i32,
            y_end: y,
            x: self.left.ceil() as i32,
            y,
        }
    }

    /// Iterate over integer pixel locations along the bottom edge.
    fn bottom_edge(&self) -> PixelIter {
        let y = self.bottom.floor() as i32;
        PixelIter {
            x_start: self.left.ceil() as i32,
            x_end: self.right.floor() as i32,
            y_end: y,
            x: self.left.ceil() as i32,
            y,
        }
    }

    /// Iterate over integer pixel locations along the left edge.
    fn left_edge(&self) -> PixelIter {
        let x = self.left.ceil() as i32;
        PixelIter {
            x_start: x,
            x_end: x,
            y_end: self.bottom.floor() as i32,
            x,
            y: self.top.ceil() as i32,
        }
    }

    /// Iterate over integer pixel locations along the right edge.
    fn right_edge(&self) -> PixelIter {
        let x = self.right.floor() as i32;
        PixelIter {
            x_start: x,
            x_end: x,
            y_end: self.bottom.floor() as i32,
            x,
            y: self.top.ceil() as i32,
        }
    }

    /// Iterate over all integer pixel locations contained within this rectangle.
    fn __iter__(&self) -> PixelIter {
        let x_start = self.left.ceil() as i32;
        let x_end = self.right.floor() as i32;
        let y_start = self.top.ceil() as i32;
        let y_end = self.bottom.floor() as i32;
        PixelIter {
            x_start,
            x_end,
            y_end,
            x: x_start,
            y: y_start,
        }
    }

    fn __len__(&self) -> usize {
        let x_count = (self.right.floor() as i32) - (self.left.ceil() as i32) + 1;
        let y_count = (self.bottom.floor() as i32) - (self.top.ceil() as i32) + 1;
        if x_count <= 0 || y_count <= 0 {
            0
        } else {
            (x_count as usize) * (y_count as usize)
        }
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
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Point {
    #[pyo3(get)]
    pub x: f32,
    #[pyo3(get)]
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

    fn __add__(&self, other: &Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }

    fn __sub__(&self, other: &Point) -> Point {
        Point {
            x: self.x - other.x,
            y: self.y - other.y,
        }
    }

    fn __mul__(&self, scalar: f32) -> Point {
        Point {
            x: self.x * scalar,
            y: self.y * scalar,
        }
    }

    fn __rmul__(&self, scalar: f32) -> Point {
        self.__mul__(scalar)
    }

    fn __truediv__(&self, scalar: f32) -> Point {
        Point {
            x: self.x / scalar,
            y: self.y / scalar,
        }
    }

    fn __neg__(&self) -> Point {
        Point {
            x: -self.x,
            y: -self.y,
        }
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
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Line {
    #[pyo3(get)]
    pub start: f32,
    #[pyo3(get)]
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

    /// The length of the line segment (end - start).
    #[getter]
    fn length(&self) -> f32 {
        self.end - self.start
    }

    /// Check if a value is contained within this line segment.
    fn contains(&self, value: f32) -> bool {
        value >= self.start && value <= self.end
    }

    /// Iterate over integer values contained within this line segment.
    fn __iter__(&self) -> IntIter {
        IntIter {
            current: self.start.ceil() as i32,
            end: self.end.floor() as i32,
        }
    }

    fn __len__(&self) -> usize {
        let count = (self.end.floor() as i32) - (self.start.ceil() as i32) + 1;
        if count <= 0 {
            0
        } else {
            count as usize
        }
    }
}

/// Iterator over a range of integer values.
#[pyclass(module = "waxy")]
struct IntIter {
    current: i32,
    end: i32,
}

#[pymethods]
impl IntIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> Option<f32> {
        if self.current > self.end {
            return None;
        }
        let val = self.current as f32;
        self.current += 1;
        Some(val)
    }
}

/// Iterator over integer pixel locations within a Rect.
#[pyclass(module = "waxy")]
struct PixelIter {
    x_start: i32,
    x_end: i32,
    y_end: i32,
    x: i32,
    y: i32,
}

#[pymethods]
impl PixelIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> Option<Point> {
        if self.x > self.x_end || self.y > self.y_end {
            return None;
        }
        let point = Point {
            x: self.x as f32,
            y: self.y as f32,
        };
        self.x += 1;
        if self.x > self.x_end {
            self.x = self.x_start;
            self.y += 1;
        }
        Some(point)
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Size>()?;
    m.add_class::<Rect>()?;
    m.add_class::<Point>()?;
    m.add_class::<Line>()?;
    Ok(())
}
