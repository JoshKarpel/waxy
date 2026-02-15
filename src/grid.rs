use pyo3::prelude::*;
use taffy::geometry::MinMax;
use taffy::prelude::TaffyGridLine;
use taffy::style::{
    GridPlacement as TaffyGridPlacement, MaxTrackSizingFunction, MinTrackSizingFunction,
    TrackSizingFunction,
};

/// A track sizing function for grid layouts (minmax(min, max)).
#[pyclass(unsendable, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridTrack {
    pub(crate) inner: TrackSizingFunction,
}

#[pymethods]
impl GridTrack {
    /// Create a fixed-size track from a length in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::length(value),
                max: MaxTrackSizingFunction::length(value),
            },
        }
    }

    /// Create a fixed-size track from a percentage.
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::percent(value),
                max: MaxTrackSizingFunction::percent(value),
            },
        }
    }

    /// Create a flexible track (fr unit).
    #[staticmethod]
    fn flex(value: f32) -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::fr(value),
            },
        }
    }

    /// Create an auto-sized track.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::auto(),
            },
        }
    }

    /// Create a min-content track.
    #[staticmethod]
    fn min_content() -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::min_content(),
                max: MaxTrackSizingFunction::min_content(),
            },
        }
    }

    /// Create a max-content track.
    #[staticmethod]
    fn max_content() -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::max_content(),
                max: MaxTrackSizingFunction::max_content(),
            },
        }
    }

    /// Create a minmax track with separate min and max sizing functions.
    #[staticmethod]
    #[pyo3(signature = (min_value, max_value))]
    fn minmax(min_value: &GridTrackMin, max_value: &GridTrackMax) -> Self {
        Self {
            inner: MinMax {
                min: min_value.inner,
                max: max_value.inner,
            },
        }
    }

    /// Create a fit-content track with a pixel limit.
    #[staticmethod]
    fn fit_content_px(limit: f32) -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::fit_content_px(limit),
            },
        }
    }

    /// Create a fit-content track with a percentage limit.
    #[staticmethod]
    fn fit_content_percent(limit: f32) -> Self {
        Self {
            inner: MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::fit_content_percent(limit),
            },
        }
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.inner)
    }
}

/// Min track sizing function (for use with GridTrack.minmax).
#[pyclass(unsendable, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridTrackMin {
    pub(crate) inner: MinTrackSizingFunction,
}

#[pymethods]
impl GridTrackMin {
    /// Create a fixed min size from a length in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: MinTrackSizingFunction::length(value),
        }
    }

    /// Create a fixed min size from a percentage.
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: MinTrackSizingFunction::percent(value),
        }
    }

    /// Create an auto min size.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: MinTrackSizingFunction::auto(),
        }
    }

    /// Create a min-content min size.
    #[staticmethod]
    fn min_content() -> Self {
        Self {
            inner: MinTrackSizingFunction::min_content(),
        }
    }

    /// Create a max-content min size.
    #[staticmethod]
    fn max_content() -> Self {
        Self {
            inner: MinTrackSizingFunction::max_content(),
        }
    }
}

/// Max track sizing function (for use with GridTrack.minmax).
#[pyclass(unsendable, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridTrackMax {
    pub(crate) inner: MaxTrackSizingFunction,
}

#[pymethods]
impl GridTrackMax {
    /// Create a fixed max size from a length in pixels.
    #[staticmethod]
    fn length(value: f32) -> Self {
        Self {
            inner: MaxTrackSizingFunction::length(value),
        }
    }

    /// Create a fixed max size from a percentage.
    #[staticmethod]
    fn percent(value: f32) -> Self {
        Self {
            inner: MaxTrackSizingFunction::percent(value),
        }
    }

    /// Create an auto max size.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: MaxTrackSizingFunction::auto(),
        }
    }

    /// Create a min-content max size.
    #[staticmethod]
    fn min_content() -> Self {
        Self {
            inner: MaxTrackSizingFunction::min_content(),
        }
    }

    /// Create a max-content max size.
    #[staticmethod]
    fn max_content() -> Self {
        Self {
            inner: MaxTrackSizingFunction::max_content(),
        }
    }

    /// Create a fractional max size (fr unit).
    #[staticmethod]
    fn fr(value: f32) -> Self {
        Self {
            inner: MaxTrackSizingFunction::fr(value),
        }
    }

    /// Create a fit-content max size with a pixel limit.
    #[staticmethod]
    fn fit_content_px(limit: f32) -> Self {
        Self {
            inner: MaxTrackSizingFunction::fit_content_px(limit),
        }
    }

    /// Create a fit-content max size with a percentage limit.
    #[staticmethod]
    fn fit_content_percent(limit: f32) -> Self {
        Self {
            inner: MaxTrackSizingFunction::fit_content_percent(limit),
        }
    }
}

/// Grid placement for a child item.
#[pyclass(unsendable, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridPlacement {
    pub(crate) inner: TaffyGridPlacement,
}

#[pymethods]
impl GridPlacement {
    /// Auto placement.
    #[staticmethod]
    fn auto() -> Self {
        Self {
            inner: TaffyGridPlacement::Auto,
        }
    }

    /// Place at a specific line index (1-based, negative counts from end).
    #[staticmethod]
    fn line(index: i16) -> Self {
        Self {
            inner: TaffyGridPlacement::from_line_index(index),
        }
    }

    /// Span a number of tracks.
    #[staticmethod]
    fn span(count: u16) -> Self {
        Self {
            inner: TaffyGridPlacement::Span(count),
        }
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.inner)
    }
}

impl From<TaffyGridPlacement> for GridPlacement {
    fn from(gp: TaffyGridPlacement) -> Self {
        Self { inner: gp }
    }
}

impl From<&GridPlacement> for TaffyGridPlacement {
    fn from(gp: &GridPlacement) -> Self {
        gp.inner.clone()
    }
}

/// A line with start and end grid placements.
#[pyclass(unsendable, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridLine {
    #[pyo3(get, set)]
    pub start: GridPlacement,
    #[pyo3(get, set)]
    pub end: GridPlacement,
}

#[pymethods]
impl GridLine {
    #[new]
    #[pyo3(signature = (start=None, end=None))]
    fn new(start: Option<GridPlacement>, end: Option<GridPlacement>) -> Self {
        Self {
            start: start.unwrap_or_else(GridPlacement::auto),
            end: end.unwrap_or_else(GridPlacement::auto),
        }
    }

    fn __repr__(&self) -> String {
        format!("GridLine(start={:?}, end={:?})", self.start, self.end)
    }
}

impl From<taffy::Line<TaffyGridPlacement>> for GridLine {
    fn from(line: taffy::Line<TaffyGridPlacement>) -> Self {
        Self {
            start: line.start.into(),
            end: line.end.into(),
        }
    }
}

impl From<&GridLine> for taffy::Line<TaffyGridPlacement> {
    fn from(line: &GridLine) -> Self {
        taffy::Line {
            start: (&line.start).into(),
            end: (&line.end).into(),
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GridTrack>()?;
    m.add_class::<GridTrackMin>()?;
    m.add_class::<GridTrackMax>()?;
    m.add_class::<GridPlacement>()?;
    m.add_class::<GridLine>()?;
    Ok(())
}
