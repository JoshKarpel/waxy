use pyo3::prelude::*;
use pyo3::types::PyTuple;
use taffy::geometry::MinMax;
use taffy::prelude::TaffyGridLine;
use taffy::style::{
    CompactLength, GridPlacement as TaffyGridPlacement, MaxTrackSizingFunction,
    MinTrackSizingFunction, TrackSizingFunction,
};

use crate::errors::InvalidPercent;

// ─── Shared value types ────────────────────────────────────────────────────

/// A length value in pixels.
///
/// Used for `size_*`, `min_size_*`, `max_size_*`, `flex_basis`, `padding_*`,
/// `border_*`, `gap_*`, `margin_*`, `inset_*`, and grid track sizing.
///
/// See: [taffy `Dimension::Length`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html),
/// [MDN `<length>`](https://developer.mozilla.org/en-US/docs/Web/CSS/length)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Length {
    #[pyo3(get)]
    pub value: f32,
}

#[pymethods]
impl Length {
    #[new]
    pub fn new(value: f32) -> Self {
        Self { value }
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["value"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("Length({})", self.value)
    }

    fn __eq__(&self, other: &Length) -> bool {
        self.value.to_bits() == other.value.to_bits()
    }

    fn __hash__(&self) -> u64 {
        self.value.to_bits() as u64
    }
}

/// A percentage value (0.0 to 1.0).
///
/// Used for `size_*`, `min_size_*`, `max_size_*`, `flex_basis`, `padding_*`,
/// `border_*`, `gap_*`, `margin_*`, `inset_*`, and grid track sizing.
///
/// Raises [`InvalidPercent`] (a subclass of both [`WaxyException`] and `ValueError`)
/// if `value` is outside the range `[0.0, 1.0]`.
///
/// See: [taffy `Dimension::Percent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html),
/// [MDN `<percentage>`](https://developer.mozilla.org/en-US/docs/Web/CSS/percentage)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Percent {
    #[pyo3(get)]
    pub value: f32,
}

#[pymethods]
impl Percent {
    #[new]
    pub fn new(value: f32) -> PyResult<Self> {
        if !(0.0..=1.0).contains(&value) {
            return Err(InvalidPercent::new_err(format!(
                "Percent value must be in [0.0, 1.0], got {value}"
            )));
        }
        Ok(Self { value })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["value"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("Percent({})", self.value)
    }

    fn __eq__(&self, other: &Percent) -> bool {
        self.value.to_bits() == other.value.to_bits()
    }

    fn __hash__(&self) -> u64 {
        self.value.to_bits() as u64
    }
}

/// Automatic sizing or placement.
///
/// Used for `size_*`, `min_size_*`, `max_size_*`, `flex_basis`, `margin_*`,
/// `inset_*`, and grid track and placement contexts.
///
/// See: [taffy `Dimension::Auto`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Auto {}

#[pymethods]
impl Auto {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "Auto()".to_owned()
    }

    fn __eq__(&self, _other: &Auto) -> bool {
        true
    }

    fn __hash__(&self) -> u64 {
        0
    }
}

/// CSS `min-content` intrinsic sizing.
///
/// The smallest size that can fit the item's contents with all soft
/// line-wrapping opportunities taken.
///
/// Used in available space (measure functions) and grid track sizing.
///
/// See: [taffy `MinTrackSizingFunction::MinContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html),
/// [MDN `min-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/min-content)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct MinContent {}

#[pymethods]
impl MinContent {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "MinContent()".to_owned()
    }

    fn __eq__(&self, _other: &MinContent) -> bool {
        true
    }

    fn __hash__(&self) -> u64 {
        1
    }
}

/// CSS `max-content` intrinsic sizing.
///
/// The smallest size that can fit the item's contents with no soft
/// line-wrapping opportunities taken.
///
/// Used in available space (measure functions) and grid track sizing.
///
/// See: [taffy `MinTrackSizingFunction::MaxContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html),
/// [MDN `max-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/max-content)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct MaxContent {}

#[pymethods]
impl MaxContent {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "MaxContent()".to_owned()
    }

    fn __eq__(&self, _other: &MaxContent) -> bool {
        true
    }

    fn __hash__(&self) -> u64 {
        2
    }
}

// ─── Available space only ──────────────────────────────────────────────────

/// A definite available space in pixels.
///
/// Used only in `AvailableSize` (measure function input) to represent
/// a concrete pixel measurement of available space.
///
/// See: [taffy `AvailableSpace::Definite`](https://docs.rs/taffy/0.9.2/taffy/style/enum.AvailableSpace.html)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Definite {
    #[pyo3(get)]
    pub value: f32,
}

#[pymethods]
impl Definite {
    #[new]
    pub fn new(value: f32) -> Self {
        Self { value }
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["value"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("Definite({})", self.value)
    }

    fn __eq__(&self, other: &Definite) -> bool {
        self.value.to_bits() == other.value.to_bits()
    }

    fn __hash__(&self) -> u64 {
        self.value.to_bits() as u64
    }
}

// ─── Grid track sizing only ────────────────────────────────────────────────

/// A fractional unit of remaining grid space (CSS `fr` unit).
///
/// After fixed lengths and percentages are allocated, remaining space is
/// divided among fractional tracks proportionally. For example, `Fraction(1)`
/// and `Fraction(2)` in the same grid get 1/3 and 2/3 of remaining space.
///
/// Used only in grid track sizing (`grid_template_*`, `grid_auto_*`).
///
/// See: [taffy `MaxTrackSizingFunction::Fraction`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html),
/// [MDN `<flex>` (`fr` unit)](https://developer.mozilla.org/en-US/docs/Web/CSS/flex_value)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Fraction {
    #[pyo3(get)]
    pub value: f32,
}

#[pymethods]
impl Fraction {
    #[new]
    pub fn new(value: f32) -> Self {
        Self { value }
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["value"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("Fraction({})", self.value)
    }

    fn __eq__(&self, other: &Fraction) -> bool {
        self.value.to_bits() == other.value.to_bits()
    }

    fn __hash__(&self) -> u64 {
        self.value.to_bits() as u64
    }
}

/// CSS `fit-content()` grid track sizing function.
///
/// Grows up to a specified limit, then clamps: `max(min_content, min(max_content, limit))`.
///
/// `limit` must be a `Length` or `Percent`.
///
/// Used only in grid track sizing.
///
/// See: [taffy `MaxTrackSizingFunction::FitContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html),
/// [MDN `fit-content()`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content_function)
#[pyclass(frozen, module = "waxy")]
#[derive(Debug)]
pub struct FitContent {
    /// Length | Percent stored as PyObject
    pub(crate) limit: Py<PyAny>,
}

#[pymethods]
impl FitContent {
    #[new]
    pub fn new(limit: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Validate limit is Length or Percent
        let _: LengthPercentageInput = limit.extract()?;
        Ok(Self {
            limit: limit.clone().unbind(),
        })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["limit"]).unwrap().unbind()
    }

    #[getter]
    fn limit(&self, py: Python<'_>) -> Py<PyAny> {
        self.limit.clone_ref(py)
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let limit_repr = self.limit.bind(py).repr()?.to_str()?.to_owned();
        Ok(format!("FitContent({limit_repr})"))
    }

    fn __eq__(&self, py: Python<'_>, other: &FitContent) -> PyResult<bool> {
        self.limit.bind(py).eq(other.limit.bind(py))
    }

    fn __hash__(&self, py: Python<'_>) -> PyResult<isize> {
        self.limit.bind(py).hash()
    }
}

impl FitContent {
    pub(crate) fn to_taffy_max(&self, py: Python<'_>) -> MaxTrackSizingFunction {
        let limit = self.limit.bind(py);
        if let Ok(l) = limit.extract::<PyRef<Length>>() {
            MaxTrackSizingFunction::fit_content_px(l.value)
        } else if let Ok(p) = limit.extract::<PyRef<Percent>>() {
            MaxTrackSizingFunction::fit_content_percent(p.value)
        } else {
            unreachable!("FitContent limit validated at construction to be Length or Percent")
        }
    }
}

/// CSS `minmax()` grid track sizing function.
///
/// Defines a size range: `min` sets the minimum track size, `max` sets the maximum.
///
/// - `min`: `Length | Percent | Auto | MinContent | MaxContent`
/// - `max`: `Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent`
///
/// Used only in grid track sizing.
///
/// See: [taffy `TrackSizingFunction`](https://docs.rs/taffy/0.9.2/taffy/style/enum.TrackSizingFunction.html),
/// [MDN `minmax()`](https://developer.mozilla.org/en-US/docs/Web/CSS/minmax)
#[pyclass(frozen, module = "waxy")]
#[derive(Debug)]
pub struct Minmax {
    /// Length | Percent | Auto | MinContent | MaxContent
    pub(crate) min: Py<PyAny>,
    /// Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent
    pub(crate) max: Py<PyAny>,
}

#[pymethods]
impl Minmax {
    #[new]
    pub fn new(min: &Bound<'_, PyAny>, max: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Validate types
        let _: GridTrackMinInput = min.extract()?;
        let _: GridTrackMaxInput = max.extract()?;
        Ok(Self {
            min: min.clone().unbind(),
            max: max.clone().unbind(),
        })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["min", "max"]).unwrap().unbind()
    }

    #[getter]
    fn min(&self, py: Python<'_>) -> Py<PyAny> {
        self.min.clone_ref(py)
    }

    #[getter]
    fn max(&self, py: Python<'_>) -> Py<PyAny> {
        self.max.clone_ref(py)
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let min_repr = self.min.bind(py).repr()?.to_str()?.to_owned();
        let max_repr = self.max.bind(py).repr()?.to_str()?.to_owned();
        Ok(format!("Minmax({min_repr}, {max_repr})"))
    }

    fn __eq__(&self, py: Python<'_>, other: &Minmax) -> PyResult<bool> {
        let min_eq = self.min.bind(py).eq(other.min.bind(py))?;
        let max_eq = self.max.bind(py).eq(other.max.bind(py))?;
        Ok(min_eq && max_eq)
    }

    fn __hash__(&self, py: Python<'_>) -> PyResult<isize> {
        let h1 = self.min.bind(py).hash()?;
        let h2 = self.max.bind(py).hash()?;
        Ok(h1 ^ h2.wrapping_shl(8))
    }
}

impl Minmax {
    pub(crate) fn to_taffy_track(&self, py: Python<'_>) -> TrackSizingFunction {
        let min_input: GridTrackMinInput = self.min.bind(py).extract().unwrap();
        let max_input: GridTrackMaxInput = self.max.bind(py).extract().unwrap();
        MinMax {
            min: min_input.to_taffy_min(),
            max: max_input.to_taffy_max(py),
        }
    }
}

// ─── Grid placement only ──────────────────────────────────────────────────

/// A 1-based grid line index (negative indices count from the end).
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::Line`](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html),
/// [MDN Line-based placement](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_line-based_placement)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct GridLine {
    #[pyo3(get)]
    pub index: i16,
}

#[pymethods]
impl GridLine {
    #[new]
    pub fn new(index: i16) -> Self {
        Self { index }
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["index"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("GridLine({})", self.index)
    }

    fn __eq__(&self, other: &GridLine) -> bool {
        self.index == other.index
    }

    fn __hash__(&self) -> i16 {
        self.index
    }
}

/// Span a number of grid tracks.
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::Span`](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html),
/// [MDN `grid-column-start` (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column-start)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct GridSpan {
    #[pyo3(get)]
    pub count: u16,
}

#[pymethods]
impl GridSpan {
    #[new]
    pub fn new(count: u16) -> Self {
        Self { count }
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["count"]).unwrap().unbind()
    }

    fn __repr__(&self) -> String {
        format!("GridSpan({})", self.count)
    }

    fn __eq__(&self, other: &GridSpan) -> bool {
        self.count == other.count
    }

    fn __hash__(&self) -> u16 {
        self.count
    }
}

// ─── Grid placement ────────────────────────────────────────────────────────

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

// ─── Input enums (FromPyObject, not pyclasses) ─────────────────────────────

/// Accepts `Length | Percent | Auto` from Python.
#[derive(FromPyObject)]
pub enum DimensionInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
}

impl DimensionInput {
    pub fn to_taffy(&self) -> taffy::Dimension {
        match self {
            DimensionInput::Length(l) => taffy::Dimension::length(l.value),
            DimensionInput::Percent(p) => taffy::Dimension::percent(p.value),
            DimensionInput::Auto(_) => taffy::Dimension::auto(),
        }
    }
}

/// Accepts `Length | Percent` from Python.
#[derive(FromPyObject)]
pub enum LengthPercentageInput {
    Length(Length),
    Percent(Percent),
}

impl LengthPercentageInput {
    pub fn to_taffy(&self) -> taffy::LengthPercentage {
        match self {
            LengthPercentageInput::Length(l) => taffy::LengthPercentage::length(l.value),
            LengthPercentageInput::Percent(p) => taffy::LengthPercentage::percent(p.value),
        }
    }
}

/// Accepts `Length | Percent | Auto` from Python (for margin/inset fields).
#[derive(FromPyObject)]
pub enum LengthPercentageAutoInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
}

impl LengthPercentageAutoInput {
    pub fn to_taffy(&self) -> taffy::LengthPercentageAuto {
        match self {
            LengthPercentageAutoInput::Length(l) => taffy::LengthPercentageAuto::length(l.value),
            LengthPercentageAutoInput::Percent(p) => taffy::LengthPercentageAuto::percent(p.value),
            LengthPercentageAutoInput::Auto(_) => taffy::LengthPercentageAuto::auto(),
        }
    }
}

/// Accepts `Definite | MinContent | MaxContent` from Python.
#[derive(FromPyObject)]
pub enum AvailableSpaceInput {
    Definite(Definite),
    MinContent(MinContent),
    MaxContent(MaxContent),
}

impl AvailableSpaceInput {
    pub fn to_taffy(&self) -> taffy::AvailableSpace {
        match self {
            AvailableSpaceInput::Definite(d) => taffy::AvailableSpace::Definite(d.value),
            AvailableSpaceInput::MinContent(_) => taffy::AvailableSpace::MinContent,
            AvailableSpaceInput::MaxContent(_) => taffy::AvailableSpace::MaxContent,
        }
    }
}

/// Accepts `Length | Percent | Auto | MinContent | MaxContent` — min side of minmax().
#[derive(FromPyObject)]
pub enum GridTrackMinInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
    MinContent(MinContent),
    MaxContent(MaxContent),
}

impl GridTrackMinInput {
    pub fn to_taffy_min(&self) -> MinTrackSizingFunction {
        match self {
            GridTrackMinInput::Length(l) => MinTrackSizingFunction::length(l.value),
            GridTrackMinInput::Percent(p) => MinTrackSizingFunction::percent(p.value),
            GridTrackMinInput::Auto(_) => MinTrackSizingFunction::auto(),
            GridTrackMinInput::MinContent(_) => MinTrackSizingFunction::min_content(),
            GridTrackMinInput::MaxContent(_) => MinTrackSizingFunction::max_content(),
        }
    }
}

/// Accepts `Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent` — max side of minmax().
#[derive(FromPyObject)]
pub enum GridTrackMaxInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
    MinContent(MinContent),
    MaxContent(MaxContent),
    Fraction(Fraction),
    FitContent(Py<FitContent>),
}

impl GridTrackMaxInput {
    pub fn to_taffy_max(&self, py: Python<'_>) -> MaxTrackSizingFunction {
        match self {
            GridTrackMaxInput::Length(l) => MaxTrackSizingFunction::length(l.value),
            GridTrackMaxInput::Percent(p) => MaxTrackSizingFunction::percent(p.value),
            GridTrackMaxInput::Auto(_) => MaxTrackSizingFunction::auto(),
            GridTrackMaxInput::MinContent(_) => MaxTrackSizingFunction::min_content(),
            GridTrackMaxInput::MaxContent(_) => MaxTrackSizingFunction::max_content(),
            GridTrackMaxInput::Fraction(f) => MaxTrackSizingFunction::fr(f.value),
            GridTrackMaxInput::FitContent(fc) => fc.bind(py).borrow().to_taffy_max(py),
        }
    }
}

/// Accepts the full set of grid track values from Python.
#[derive(FromPyObject)]
pub enum GridTrackInput {
    Length(Length),
    Percent(Percent),
    Auto(Auto),
    MinContent(MinContent),
    MaxContent(MaxContent),
    Fraction(Fraction),
    Minmax(Py<Minmax>),
    FitContent(Py<FitContent>),
}

impl GridTrackInput {
    pub fn to_taffy(&self, py: Python<'_>) -> TrackSizingFunction {
        match self {
            GridTrackInput::Length(l) => MinMax {
                min: MinTrackSizingFunction::length(l.value),
                max: MaxTrackSizingFunction::length(l.value),
            },
            GridTrackInput::Percent(p) => MinMax {
                min: MinTrackSizingFunction::percent(p.value),
                max: MaxTrackSizingFunction::percent(p.value),
            },
            GridTrackInput::Auto(_) => MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::auto(),
            },
            GridTrackInput::MinContent(_) => MinMax {
                min: MinTrackSizingFunction::min_content(),
                max: MaxTrackSizingFunction::min_content(),
            },
            GridTrackInput::MaxContent(_) => MinMax {
                min: MinTrackSizingFunction::max_content(),
                max: MaxTrackSizingFunction::max_content(),
            },
            GridTrackInput::Fraction(f) => MinMax {
                min: MinTrackSizingFunction::auto(),
                max: MaxTrackSizingFunction::fr(f.value),
            },
            GridTrackInput::Minmax(mm) => mm.bind(py).borrow().to_taffy_track(py),
            GridTrackInput::FitContent(fc) => MinMax {
                min: MinTrackSizingFunction::auto(),
                max: fc.bind(py).borrow().to_taffy_max(py),
            },
        }
    }
}

/// Accepts `GridLine | GridSpan | Auto` for grid placement.
#[derive(FromPyObject)]
pub enum GridPlacementInput {
    GridLine(GridLine),
    GridSpan(GridSpan),
    Auto(Auto),
}

impl GridPlacementInput {
    pub fn to_taffy(&self) -> TaffyGridPlacement {
        match self {
            GridPlacementInput::GridLine(gl) => TaffyGridPlacement::from_line_index(gl.index),
            GridPlacementInput::GridSpan(gs) => TaffyGridPlacement::Span(gs.count),
            GridPlacementInput::Auto(_) => TaffyGridPlacement::Auto,
        }
    }
}

// ─── Taffy → Python conversion helpers ────────────────────────────────────
// These helpers bypass `Percent::new()` validation and construct `Percent` directly.
// This is intentional: Taffy only stores values that were originally inserted by us,
// and all user-facing Percent construction goes through `Percent::new()` which validates
// the [0.0, 1.0] range. Values round-tripped through Taffy are guaranteed to be valid.

pub fn dimension_to_py(py: Python<'_>, d: taffy::Dimension) -> PyResult<Py<PyAny>> {
    let raw = d.into_raw();
    match raw.tag() {
        CompactLength::LENGTH_TAG => Ok(Py::new(py, Length { value: raw.value() })?.into_any()),
        CompactLength::PERCENT_TAG => Ok(Py::new(py, Percent { value: raw.value() })?.into_any()),
        CompactLength::AUTO_TAG => Ok(Py::new(py, Auto {})?.into_any()),
        _ => Ok(Py::new(py, Auto {})?.into_any()),
    }
}

pub fn length_percentage_to_py(py: Python<'_>, lp: taffy::LengthPercentage) -> PyResult<Py<PyAny>> {
    let raw = lp.into_raw();
    match raw.tag() {
        CompactLength::LENGTH_TAG => Ok(Py::new(py, Length { value: raw.value() })?.into_any()),
        CompactLength::PERCENT_TAG => Ok(Py::new(py, Percent { value: raw.value() })?.into_any()),
        _ => Ok(Py::new(py, Length { value: 0.0 })?.into_any()),
    }
}

pub fn length_percentage_auto_to_py(
    py: Python<'_>,
    lpa: taffy::LengthPercentageAuto,
) -> PyResult<Py<PyAny>> {
    let raw = lpa.into_raw();
    match raw.tag() {
        CompactLength::LENGTH_TAG => Ok(Py::new(py, Length { value: raw.value() })?.into_any()),
        CompactLength::PERCENT_TAG => Ok(Py::new(py, Percent { value: raw.value() })?.into_any()),
        CompactLength::AUTO_TAG => Ok(Py::new(py, Auto {})?.into_any()),
        _ => Ok(Py::new(py, Auto {})?.into_any()),
    }
}

pub fn available_space_to_py(py: Python<'_>, a: taffy::AvailableSpace) -> PyResult<Py<PyAny>> {
    match a {
        taffy::AvailableSpace::Definite(v) => Ok(Py::new(py, Definite { value: v })?.into_any()),
        taffy::AvailableSpace::MinContent => Ok(Py::new(py, MinContent {})?.into_any()),
        taffy::AvailableSpace::MaxContent => Ok(Py::new(py, MaxContent {})?.into_any()),
    }
}

fn grid_track_min_to_py(py: Python<'_>, min: MinTrackSizingFunction) -> PyResult<Py<PyAny>> {
    let raw = min.into_raw();
    match raw.tag() {
        CompactLength::LENGTH_TAG => Ok(Py::new(py, Length { value: raw.value() })?.into_any()),
        CompactLength::PERCENT_TAG => Ok(Py::new(py, Percent { value: raw.value() })?.into_any()),
        CompactLength::AUTO_TAG => Ok(Py::new(py, Auto {})?.into_any()),
        CompactLength::MIN_CONTENT_TAG => Ok(Py::new(py, MinContent {})?.into_any()),
        CompactLength::MAX_CONTENT_TAG => Ok(Py::new(py, MaxContent {})?.into_any()),
        _ => Ok(Py::new(py, Auto {})?.into_any()),
    }
}

fn grid_track_max_to_py(py: Python<'_>, max: MaxTrackSizingFunction) -> PyResult<Py<PyAny>> {
    let raw = max.into_raw();
    match raw.tag() {
        CompactLength::LENGTH_TAG => Ok(Py::new(py, Length { value: raw.value() })?.into_any()),
        CompactLength::PERCENT_TAG => Ok(Py::new(py, Percent { value: raw.value() })?.into_any()),
        CompactLength::AUTO_TAG => Ok(Py::new(py, Auto {})?.into_any()),
        CompactLength::MIN_CONTENT_TAG => Ok(Py::new(py, MinContent {})?.into_any()),
        CompactLength::MAX_CONTENT_TAG => Ok(Py::new(py, MaxContent {})?.into_any()),
        CompactLength::FR_TAG => Ok(Py::new(py, Fraction { value: raw.value() })?.into_any()),
        CompactLength::FIT_CONTENT_PX_TAG => {
            let limit = Py::new(py, Length { value: raw.value() })?.into_any();
            Ok(Py::new(py, FitContent { limit })?.into_any())
        }
        CompactLength::FIT_CONTENT_PERCENT_TAG => {
            let limit = Py::new(py, Percent { value: raw.value() })?.into_any();
            Ok(Py::new(py, FitContent { limit })?.into_any())
        }
        _ => Ok(Py::new(py, Auto {})?.into_any()),
    }
}

pub fn grid_track_to_py(py: Python<'_>, tsf: TrackSizingFunction) -> PyResult<Py<PyAny>> {
    let min = tsf.min_sizing_function();
    let max = tsf.max_sizing_function();
    let min_raw = min.into_raw();
    let max_raw = max.into_raw();

    // Shorthand recognition: common patterns return the simpler type
    match (min_raw.tag(), max_raw.tag()) {
        // length(v) == minmax(length(v), length(v))
        (CompactLength::LENGTH_TAG, CompactLength::LENGTH_TAG)
            if min_raw.value().to_bits() == max_raw.value().to_bits() =>
        {
            Ok(Py::new(
                py,
                Length {
                    value: min_raw.value(),
                },
            )?
            .into_any())
        }
        // percent(v) == minmax(percent(v), percent(v))
        (CompactLength::PERCENT_TAG, CompactLength::PERCENT_TAG)
            if min_raw.value().to_bits() == max_raw.value().to_bits() =>
        {
            Ok(Py::new(
                py,
                Percent {
                    value: min_raw.value(),
                },
            )?
            .into_any())
        }
        // auto == minmax(auto, auto)
        (CompactLength::AUTO_TAG, CompactLength::AUTO_TAG) => Ok(Py::new(py, Auto {})?.into_any()),
        // min_content == minmax(min_content, min_content)
        (CompactLength::MIN_CONTENT_TAG, CompactLength::MIN_CONTENT_TAG) => {
            Ok(Py::new(py, MinContent {})?.into_any())
        }
        // max_content == minmax(max_content, max_content)
        (CompactLength::MAX_CONTENT_TAG, CompactLength::MAX_CONTENT_TAG) => {
            Ok(Py::new(py, MaxContent {})?.into_any())
        }
        // fr(v) == minmax(auto, fr(v))
        (CompactLength::AUTO_TAG, CompactLength::FR_TAG) => Ok(Py::new(
            py,
            Fraction {
                value: max_raw.value(),
            },
        )?
        .into_any()),
        // fit_content_px(v) == minmax(auto, fit_content_px(v))
        (CompactLength::AUTO_TAG, CompactLength::FIT_CONTENT_PX_TAG) => {
            let limit = Py::new(
                py,
                Length {
                    value: max_raw.value(),
                },
            )?
            .into_any();
            Ok(Py::new(py, FitContent { limit })?.into_any())
        }
        // fit_content_percent(v) == minmax(auto, fit_content_percent(v))
        (CompactLength::AUTO_TAG, CompactLength::FIT_CONTENT_PERCENT_TAG) => {
            let limit = Py::new(
                py,
                Percent {
                    value: max_raw.value(),
                },
            )?
            .into_any();
            Ok(Py::new(py, FitContent { limit })?.into_any())
        }
        // Generic minmax
        _ => {
            let min_py = grid_track_min_to_py(py, min)?;
            let max_py = grid_track_max_to_py(py, max)?;
            Ok(Py::new(
                py,
                Minmax {
                    min: min_py,
                    max: max_py,
                },
            )?
            .into_any())
        }
    }
}

pub fn grid_placement_to_py(py: Python<'_>, gp: TaffyGridPlacement) -> PyResult<Py<PyAny>> {
    match gp {
        TaffyGridPlacement::Auto => Ok(Py::new(py, Auto {})?.into_any()),
        TaffyGridPlacement::Line(gl) => {
            Ok(Py::new(py, GridLine { index: gl.as_i16() })?.into_any())
        }
        TaffyGridPlacement::Span(count) => Ok(Py::new(py, GridSpan { count })?.into_any()),
        // NamedLine and NamedSpan are not supported; map to Auto
        _ => Ok(Py::new(py, Auto {})?.into_any()),
    }
}

// ─── register ─────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Length>()?;
    m.add_class::<Percent>()?;
    m.add_class::<Auto>()?;
    m.add_class::<MinContent>()?;
    m.add_class::<MaxContent>()?;
    m.add_class::<Definite>()?;
    m.add_class::<Fraction>()?;
    m.add_class::<FitContent>()?;
    m.add_class::<Minmax>()?;
    m.add_class::<GridLine>()?;
    m.add_class::<GridSpan>()?;
    m.add_class::<GridPlacement>()?;

    // Module-level singletons for common zero-field types
    m.add("AUTO", Py::new(m.py(), Auto {})?.into_any())?;
    m.add("MIN_CONTENT", Py::new(m.py(), MinContent {})?.into_any())?;
    m.add("MAX_CONTENT", Py::new(m.py(), MaxContent {})?.into_any())?;

    Ok(())
}
