use pyo3::prelude::*;

use crate::values::{available_space_to_py, AvailableSpaceInput};

/// Normalize an f32 for hashing: maps -0.0 to +0.0 so that
/// hash is consistent with `==` equality (which treats them as equal).
pub(crate) fn hash_f32<H: std::hash::Hasher>(v: f32, hasher: &mut H) {
    use std::hash::Hash;
    // IEEE 754: -0.0 + 0.0 = +0.0 (branchless normalization)
    (v + 0.0).to_bits().hash(hasher);
}

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

    pub(crate) fn __repr__(&self) -> String {
        format!("Size(width={}, height={})", self.width, self.height)
    }

    fn __eq__(&self, other: &Size) -> bool {
        self.width == other.width && self.height == other.height
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_f32(self.width, &mut hasher);
        hash_f32(self.height, &mut hasher);
        std::hash::Hasher::finish(&hasher)
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

/// A value for each of the four sides of a box (left, right, top, bottom).
///
/// Mirrors taffy's `Rect<f32>`, which holds per-side values such as margin, padding and border
/// thicknesses, or the edges of a box.
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

    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_f32(self.left, &mut hasher);
        hash_f32(self.right, &mut hasher);
        hash_f32(self.top, &mut hasher);
        hash_f32(self.bottom, &mut hasher);
        std::hash::Hasher::finish(&hasher)
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

    pub(crate) fn __repr__(&self) -> String {
        format!("Point(x={}, y={})", self.x, self.y)
    }

    fn __eq__(&self, other: &Point) -> bool {
        self.x == other.x && self.y == other.y
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_f32(self.x, &mut hasher);
        hash_f32(self.y, &mut hasher);
        std::hash::Hasher::finish(&hasher)
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

/// A start and an end value.
///
/// Mirrors taffy's `Line<f32>`, e.g. the start and end positions of a grid track.
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

    fn __hash__(&self) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_f32(self.start, &mut hasher);
        hash_f32(self.end, &mut hasher);
        std::hash::Hasher::finish(&hasher)
    }
}

impl From<taffy::Line<f32>> for Line {
    fn from(l: taffy::Line<f32>) -> Self {
        Self {
            start: l.start,
            end: l.end,
        }
    }
}

/// Known dimensions passed to measure functions (independently-optional width/height).
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct KnownSize {
    width: Option<f32>,
    height: Option<f32>,
}

#[pymethods]
impl KnownSize {
    #[new]
    #[pyo3(signature = (width=None, height=None))]
    fn new(width: Option<f32>, height: Option<f32>) -> Self {
        Self { width, height }
    }

    fn __repr__(&self) -> String {
        format!(
            "KnownSize(width={}, height={})",
            match self.width {
                Some(v) => v.to_string(),
                None => "None".to_string(),
            },
            match self.height {
                Some(v) => v.to_string(),
                None => "None".to_string(),
            }
        )
    }

    fn __eq__(&self, other: &KnownSize) -> bool {
        self.width == other.width && self.height == other.height
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        match self.width {
            Some(v) => {
                1u8.hash(&mut hasher);
                hash_f32(v, &mut hasher);
            }
            None => 0u8.hash(&mut hasher),
        }
        match self.height {
            Some(v) => {
                1u8.hash(&mut hasher);
                hash_f32(v, &mut hasher);
            }
            None => 0u8.hash(&mut hasher),
        }
        hasher.finish()
    }

    fn __iter__(&self) -> KnownSizeIter {
        KnownSizeIter {
            width: self.width,
            height: self.height,
            index: 0,
        }
    }

    #[getter]
    fn width(&self) -> Option<f32> {
        self.width
    }

    #[getter]
    fn height(&self) -> Option<f32> {
        self.height
    }
}

impl From<taffy::Size<Option<f32>>> for KnownSize {
    fn from(s: taffy::Size<Option<f32>>) -> Self {
        Self {
            width: s.width,
            height: s.height,
        }
    }
}

#[pyclass(module = "waxy")]
struct KnownSizeIter {
    width: Option<f32>,
    height: Option<f32>,
    index: u8,
}

#[pymethods]
impl KnownSizeIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> Option<Option<f32>> {
        let val = match self.index {
            0 => Some(self.width),
            1 => Some(self.height),
            _ => None,
        };
        self.index += 1;
        val
    }
}

/// Available dimensions passed to measure functions (width/height as `Definite | MinContent | MaxContent`).
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct AvailableSize {
    width: taffy::AvailableSpace,
    height: taffy::AvailableSpace,
}

#[pymethods]
impl AvailableSize {
    #[new]
    fn new(width: AvailableSpaceInput, height: AvailableSpaceInput) -> Self {
        Self {
            width: width.to_taffy(),
            height: height.to_taffy(),
        }
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let w = available_space_to_py(py, self.width)?;
        let h = available_space_to_py(py, self.height)?;
        let w_repr = w.bind(py).repr()?.to_str()?.to_owned();
        let h_repr = h.bind(py).repr()?.to_str()?.to_owned();
        Ok(format!("AvailableSize(width={w_repr}, height={h_repr})"))
    }

    fn __eq__(&self, other: &AvailableSize) -> bool {
        self.width == other.width && self.height == other.height
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        match self.width {
            taffy::AvailableSpace::Definite(v) => {
                0u8.hash(&mut hasher);
                hash_f32(v, &mut hasher);
            }
            taffy::AvailableSpace::MinContent => 1u8.hash(&mut hasher),
            taffy::AvailableSpace::MaxContent => 2u8.hash(&mut hasher),
        }
        match self.height {
            taffy::AvailableSpace::Definite(v) => {
                0u8.hash(&mut hasher);
                hash_f32(v, &mut hasher);
            }
            taffy::AvailableSpace::MinContent => 1u8.hash(&mut hasher),
            taffy::AvailableSpace::MaxContent => 2u8.hash(&mut hasher),
        }
        hasher.finish()
    }

    fn __iter__(&self) -> AvailableSizeIter {
        AvailableSizeIter {
            width: self.width,
            height: self.height,
            index: 0,
        }
    }

    #[getter]
    fn width(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        available_space_to_py(py, self.width)
    }

    #[getter]
    fn height(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        available_space_to_py(py, self.height)
    }
}

impl From<taffy::Size<taffy::AvailableSpace>> for AvailableSize {
    fn from(s: taffy::Size<taffy::AvailableSpace>) -> Self {
        Self {
            width: s.width,
            height: s.height,
        }
    }
}

impl From<&AvailableSize> for taffy::Size<taffy::AvailableSpace> {
    fn from(a: &AvailableSize) -> Self {
        taffy::Size {
            width: a.width,
            height: a.height,
        }
    }
}

#[pyclass(module = "waxy")]
struct AvailableSizeIter {
    width: taffy::AvailableSpace,
    height: taffy::AvailableSpace,
    index: u8,
}

#[pymethods]
impl AvailableSizeIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        let val = match self.index {
            0 => Some(available_space_to_py(py, self.width)?),
            1 => Some(available_space_to_py(py, self.height)?),
            _ => None,
        };
        self.index += 1;
        Ok(val)
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Size>()?;
    m.add_class::<Rect>()?;
    m.add_class::<Point>()?;
    m.add_class::<Line>()?;
    m.add_class::<KnownSize>()?;
    m.add_class::<AvailableSize>()?;
    Ok(())
}
