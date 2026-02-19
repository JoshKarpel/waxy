use pyo3::prelude::*;
use taffy::style::GridPlacement as TaffyGridPlacement;

use crate::values::{grid_placement_to_py, GridPlacementInput};

/// A start/end pair of grid placements for a child item.
///
/// Each of `start` and `end` is a `GridLine | GridSpan | Auto` value.
/// Defaults both to `Auto` (the CSS default for unplaced items).
///
/// See: [taffy `Line<GridPlacement>`](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Line.html),
/// [MDN `grid-row`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row),
/// [MDN `grid-column`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct GridPlacement {
    pub(crate) start: TaffyGridPlacement,
    pub(crate) end: TaffyGridPlacement,
}

#[pymethods]
impl GridPlacement {
    #[new]
    #[pyo3(signature = (start=None, end=None))]
    fn new(start: Option<GridPlacementInput>, end: Option<GridPlacementInput>) -> Self {
        Self {
            start: start.map_or(TaffyGridPlacement::Auto, |v| v.to_taffy()),
            end: end.map_or(TaffyGridPlacement::Auto, |v| v.to_taffy()),
        }
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let start = grid_placement_to_py(py, self.start.clone())?;
        let end = grid_placement_to_py(py, self.end.clone())?;
        let start_repr = start.bind(py).repr()?.to_str()?.to_owned();
        let end_repr = end.bind(py).repr()?.to_str()?.to_owned();
        Ok(format!("GridPlacement(start={start_repr}, end={end_repr})"))
    }

    #[getter]
    fn start(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        grid_placement_to_py(py, self.start.clone())
    }

    #[getter]
    fn end(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        grid_placement_to_py(py, self.end.clone())
    }
}

impl From<taffy::Line<TaffyGridPlacement>> for GridPlacement {
    fn from(line: taffy::Line<TaffyGridPlacement>) -> Self {
        // line is owned so we can move start and end
        Self {
            start: line.start,
            end: line.end,
        }
    }
}

impl From<&GridPlacement> for taffy::Line<TaffyGridPlacement> {
    fn from(gp: &GridPlacement) -> Self {
        taffy::Line {
            start: gp.start.clone(),
            end: gp.end.clone(),
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GridPlacement>()?;
    Ok(())
}
