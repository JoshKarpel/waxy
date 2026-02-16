use pyo3::prelude::*;

/// A dimension value that can be a length, percentage, or auto.
#[pyclass(unsendable, frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Dimension {
    inner: taffy::Dimension,
}

#[pymethods]
impl Dimension {
    /// Create a length dimension in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: taffy::Dimension::length(value),
        }
    }

    /// Create a percentage dimension (0.0 to 1.0).
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: taffy::Dimension::percent(value),
        }
    }

    /// Create an auto dimension.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: taffy::Dimension::auto(),
        }
    }

    fn is_auto(&self) -> bool {
        self.inner.is_auto()
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.inner)
    }

    fn __eq__(&self, other: &Dimension) -> bool {
        // Compare tag and value
        self.inner.tag() == other.inner.tag() && self.inner.value() == other.inner.value()
    }
}

impl From<taffy::Dimension> for Dimension {
    fn from(d: taffy::Dimension) -> Self {
        Self { inner: d }
    }
}

impl From<&Dimension> for taffy::Dimension {
    fn from(d: &Dimension) -> Self {
        d.inner
    }
}

/// A length or percentage value (no auto).
#[pyclass(unsendable, frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct LengthPercentage {
    inner: taffy::LengthPercentage,
}

#[pymethods]
impl LengthPercentage {
    /// Create a length value in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: taffy::LengthPercentage::length(value),
        }
    }

    /// Create a percentage value (0.0 to 1.0).
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: taffy::LengthPercentage::percent(value),
        }
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.inner)
    }

    fn __eq__(&self, other: &LengthPercentage) -> bool {
        self.inner == other.inner
    }
}

impl From<taffy::LengthPercentage> for LengthPercentage {
    fn from(lp: taffy::LengthPercentage) -> Self {
        Self { inner: lp }
    }
}

impl From<&LengthPercentage> for taffy::LengthPercentage {
    fn from(lp: &LengthPercentage) -> Self {
        lp.inner
    }
}

/// A length, percentage, or auto value.
#[pyclass(unsendable, frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct LengthPercentageAuto {
    inner: taffy::LengthPercentageAuto,
}

#[pymethods]
impl LengthPercentageAuto {
    /// Create a length value in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: taffy::LengthPercentageAuto::length(value),
        }
    }

    /// Create a percentage value (0.0 to 1.0).
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: taffy::LengthPercentageAuto::percent(value),
        }
    }

    /// Create an auto value.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: taffy::LengthPercentageAuto::auto(),
        }
    }

    fn is_auto(&self) -> bool {
        self.inner.is_auto()
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.inner)
    }

    fn __eq__(&self, other: &LengthPercentageAuto) -> bool {
        self.inner == other.inner
    }
}

impl From<taffy::LengthPercentageAuto> for LengthPercentageAuto {
    fn from(lpa: taffy::LengthPercentageAuto) -> Self {
        Self { inner: lpa }
    }
}

impl From<&LengthPercentageAuto> for taffy::LengthPercentageAuto {
    fn from(lpa: &LengthPercentageAuto) -> Self {
        lpa.inner
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Dimension>()?;
    m.add_class::<LengthPercentage>()?;
    m.add_class::<LengthPercentageAuto>()?;
    Ok(())
}
