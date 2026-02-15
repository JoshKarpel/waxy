use pyo3::prelude::*;

use crate::dimensions::{Dimension, LengthPercentage};
use crate::enums::AvailableSpace;
use crate::grid::{GridTrack, GridTrackMax, GridTrackMin};

/// Create a zero-length value.
#[pyfunction]
fn zero() -> LengthPercentage {
    taffy::LengthPercentage::length(0.0).into()
}

/// Create an auto dimension.
#[pyfunction]
fn auto() -> Dimension {
    taffy::Dimension::auto().into()
}

/// Create a length dimension in pixels.
#[pyfunction]
fn length(value: f32) -> Dimension {
    taffy::Dimension::length(value).into()
}

/// Create a percentage dimension.
#[pyfunction]
fn percent(value: f32) -> Dimension {
    taffy::Dimension::percent(value).into()
}

/// Create a min-content available space.
#[pyfunction]
fn min_content() -> AvailableSpace {
    taffy::AvailableSpace::MinContent.into()
}

/// Create a max-content available space.
#[pyfunction]
fn max_content() -> AvailableSpace {
    taffy::AvailableSpace::MaxContent.into()
}

/// Create a flexible grid track (fr unit).
#[pyfunction]
fn fr(value: f32) -> GridTrack {
    use taffy::geometry::MinMax;
    use taffy::style::{MaxTrackSizingFunction, MinTrackSizingFunction};
    GridTrack {
        inner: MinMax {
            min: MinTrackSizingFunction::auto(),
            max: MaxTrackSizingFunction::fr(value),
        },
    }
}

/// Create a minmax grid track.
#[pyfunction]
fn minmax(min: &GridTrackMin, max: &GridTrackMax) -> GridTrack {
    use taffy::geometry::MinMax;
    GridTrack {
        inner: MinMax {
            min: min.inner,
            max: max.inner,
        },
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zero, m)?)?;
    m.add_function(wrap_pyfunction!(auto, m)?)?;
    m.add_function(wrap_pyfunction!(length, m)?)?;
    m.add_function(wrap_pyfunction!(percent, m)?)?;
    m.add_function(wrap_pyfunction!(min_content, m)?)?;
    m.add_function(wrap_pyfunction!(max_content, m)?)?;
    m.add_function(wrap_pyfunction!(fr, m)?)?;
    m.add_function(wrap_pyfunction!(minmax, m)?)?;
    Ok(())
}
