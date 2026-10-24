use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use taffy::geometry::MinMax;
use taffy::prelude::TaffyGridLine;
use taffy::style::{
    CompactLength, GridPlacement as TaffyGridPlacement, MaxTrackSizingFunction,
    MinTrackSizingFunction, TrackSizingFunction,
};

use crate::errors::{
    InvalidGridLine, InvalidGridSpan, InvalidGridTemplateArea, InvalidGridTemplateAreas,
    InvalidLength, InvalidPercent, InvalidRepeat,
};

// ─── Shared value types ────────────────────────────────────────────────────

/// A length value in pixels.
///
/// Used for `size_*`, `min_size_*`, `max_size_*`, `flex_basis`, `padding_*`,
/// `border_*`, `gap_*`, `margin_*`, `inset_*`, and grid track sizing.
///
/// See: [taffy `Dimension::Length`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html),
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
    pub fn new(value: f32) -> PyResult<Self> {
        if value.is_nan() {
            return Err(InvalidLength::new_err("Length value must not be NaN"));
        }
        Ok(Self { value })
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

    fn __hash__(&self) -> isize {
        self.value.to_bits() as isize
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
/// See: [taffy `Dimension::Percent`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html),
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

    fn __hash__(&self) -> isize {
        self.value.to_bits() as isize
    }
}

/// Automatic sizing or placement.
///
/// Used for `size_*`, `min_size_*`, `max_size_*`, `flex_basis`, `margin_*`,
/// `inset_*`, and grid track and placement contexts.
///
/// See: [taffy `Dimension::Auto`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html)
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

    fn __hash__(&self) -> isize {
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
/// See: [taffy `MinTrackSizingFunction::MinContent`](https://docs.rs/taffy/0.15.0/taffy/style/struct.MinTrackSizingFunction.html),
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

    fn __hash__(&self) -> isize {
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
/// See: [taffy `MinTrackSizingFunction::MaxContent`](https://docs.rs/taffy/0.15.0/taffy/style/struct.MinTrackSizingFunction.html),
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

    fn __hash__(&self) -> isize {
        2
    }
}

// ─── Size and flex basis only ──────────────────────────────────────────────

/// CSS `stretch` sizing keyword.
///
/// Fills the containing block's available space, less the node's margins.
///
/// Used only in `size_*` and `flex_basis`.
///
/// See: [taffy `Dimension::stretch`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html),
/// [MDN `stretch`](https://developer.mozilla.org/en-US/docs/Web/CSS/width#stretch)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Stretch {}

#[pymethods]
impl Stretch {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "Stretch()".to_owned()
    }

    fn __eq__(&self, _other: &Stretch) -> bool {
        true
    }

    fn __hash__(&self) -> isize {
        3
    }
}

/// CSS `fit-content` sizing keyword (without a limit).
///
/// Equivalent to `fit-content(stretch)`: the node is sized to its contents, clamped between
/// its min-content and the available space. For an explicit limit, use [`FitContent`].
///
/// Used only in `size_*` and `flex_basis`.
///
/// See: [taffy `Dimension::fit_content`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html),
/// [MDN `fit-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct FitContentKeyword {}

#[pymethods]
impl FitContentKeyword {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "FitContentKeyword()".to_owned()
    }

    fn __eq__(&self, _other: &FitContentKeyword) -> bool {
        true
    }

    fn __hash__(&self) -> isize {
        4
    }
}

/// CSS `content` flex basis keyword.
///
/// Sizes the flex item based on its content, ignoring its `size_*` in the main axis.
///
/// Used only in `flex_basis`.
///
/// See: [taffy `Dimension::content`](https://docs.rs/taffy/0.15.0/taffy/style/struct.Dimension.html),
/// [MDN `flex-basis: content`](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis#content)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct Content {}

#[pymethods]
impl Content {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "Content()".to_owned()
    }

    fn __eq__(&self, _other: &Content) -> bool {
        true
    }

    fn __hash__(&self) -> isize {
        5
    }
}

// ─── Available space only ──────────────────────────────────────────────────

/// A definite available space in pixels.
///
/// Used only in `AvailableSize` (measure function input) to represent
/// a concrete pixel measurement of available space.
///
/// See: [taffy `AvailableSpace::Definite`](https://docs.rs/taffy/0.15.0/taffy/style/enum.AvailableSpace.html)
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

    fn __hash__(&self) -> isize {
        self.value.to_bits() as isize
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
/// See: [taffy `MaxTrackSizingFunction::Fraction`](https://docs.rs/taffy/0.15.0/taffy/style/struct.MaxTrackSizingFunction.html),
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

    fn __hash__(&self) -> isize {
        self.value.to_bits() as isize
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
/// See: [taffy `MaxTrackSizingFunction::FitContent`](https://docs.rs/taffy/0.15.0/taffy/style/struct.MaxTrackSizingFunction.html),
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

    pub(crate) fn to_taffy_dimension(&self, py: Python<'_>) -> taffy::Dimension {
        let limit = self.limit.bind(py);
        if let Ok(l) = limit.extract::<PyRef<Length>>() {
            taffy::Dimension::fit_content_px(l.value)
        } else if let Ok(p) = limit.extract::<PyRef<Percent>>() {
            taffy::Dimension::fit_content_percent(p.value)
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
/// See: [taffy `TrackSizingFunction`](https://docs.rs/taffy/0.15.0/taffy/style/type.TrackSizingFunction.html),
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

/// CSS `auto-fill` repetition count: repeat as many times as fit without overflowing,
/// keeping empty tracks.
///
/// Used only as the `count` of a `Repeat`.
///
/// See: [taffy `RepetitionCount::AutoFill`](https://docs.rs/taffy/0.15.0/taffy/style/enum.RepetitionCount.html),
/// [MDN `auto-fill`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat#auto-fill)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct AutoFill {}

#[pymethods]
impl AutoFill {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "AutoFill()".to_owned()
    }

    fn __eq__(&self, _other: &AutoFill) -> bool {
        true
    }

    fn __hash__(&self) -> isize {
        6
    }
}

/// CSS `auto-fit` repetition count: like `auto-fill`, but empty repeated tracks collapse.
///
/// Used only as the `count` of a `Repeat`.
///
/// See: [taffy `RepetitionCount::AutoFit`](https://docs.rs/taffy/0.15.0/taffy/style/enum.RepetitionCount.html),
/// [MDN `auto-fit`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat#auto-fit)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct AutoFit {}

#[pymethods]
impl AutoFit {
    #[new]
    pub fn new() -> Self {
        Self {}
    }

    fn __repr__(&self) -> String {
        "AutoFit()".to_owned()
    }

    fn __eq__(&self, _other: &AutoFit) -> bool {
        true
    }

    fn __hash__(&self) -> isize {
        7
    }
}

/// CSS `repeat()` in `grid_template_rows` / `grid_template_columns`.
///
/// Repeats `tracks` `count` times. `line_names`, if given, names the lines of each repetition
/// positionally: entry `i` names the line before `tracks[i]`, and the final entry names the
/// line after the last track (so it has `len(tracks) + 1` entries).
///
/// See: [taffy `GridTemplateRepetition`](https://docs.rs/taffy/0.15.0/taffy/style/struct.GridTemplateRepetition.html),
/// [MDN `repeat()`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat)
#[pyclass(frozen, module = "waxy")]
#[derive(Debug)]
pub struct Repeat {
    count: taffy::RepetitionCount,
    /// `GridTrackValue` objects, validated at construction.
    tracks: Vec<Py<PyAny>>,
    line_names: Vec<Vec<String>>,
}

#[pymethods]
impl Repeat {
    #[new]
    #[pyo3(signature = (count, tracks, line_names=None))]
    pub fn new(
        count: RepetitionCountInput,
        tracks: Vec<Bound<'_, PyAny>>,
        line_names: Option<Vec<Vec<String>>>,
    ) -> PyResult<Self> {
        let count = match count {
            RepetitionCountInput::AutoFill(_) => taffy::RepetitionCount::AutoFill,
            RepetitionCountInput::AutoFit(_) => taffy::RepetitionCount::AutoFit,
            RepetitionCountInput::Count(0) => {
                return Err(InvalidRepeat::new_err("Repeat count must be at least 1"))
            }
            RepetitionCountInput::Count(n) => taffy::RepetitionCount::Count(n),
        };
        if tracks.is_empty() {
            return Err(InvalidRepeat::new_err(
                "Repeat must have at least one track",
            ));
        }
        for track in &tracks {
            let _: GridTrackInput = track.extract()?;
        }
        let line_names = line_names.unwrap_or_default();
        // taffy panics during layout on any other length.
        if !line_names.is_empty() && line_names.len() != tracks.len() + 1 {
            return Err(InvalidRepeat::new_err(format!(
                "Repeat line_names must be empty or have len(tracks) + 1 = {} entries, got {}",
                tracks.len() + 1,
                line_names.len()
            )));
        }
        Ok(Self {
            count,
            tracks: tracks.into_iter().map(Bound::unbind).collect(),
            line_names,
        })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["count", "tracks", "line_names"])
            .unwrap()
            .unbind()
    }

    #[getter]
    fn count(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        match self.count {
            taffy::RepetitionCount::AutoFill => into_py_any(py, AutoFill {}),
            taffy::RepetitionCount::AutoFit => into_py_any(py, AutoFit {}),
            taffy::RepetitionCount::Count(n) => Ok(n.into_pyobject(py)?.into_any().unbind()),
        }
    }

    #[getter]
    fn tracks(&self, py: Python<'_>) -> Vec<Py<PyAny>> {
        self.tracks.iter().map(|t| t.clone_ref(py)).collect()
    }

    #[getter]
    fn line_names(&self) -> Vec<Vec<String>> {
        self.line_names.clone()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let count_repr = self.count(py)?.bind(py).repr()?.to_str()?.to_owned();
        let tracks_repr = pyo3::types::PyList::new(py, self.tracks(py))?
            .repr()?
            .to_str()?
            .to_owned();
        if self.line_names.is_empty() {
            return Ok(format!("Repeat({count_repr}, {tracks_repr})"));
        }
        let names_repr = self
            .line_names
            .clone()
            .into_pyobject(py)?
            .repr()?
            .to_str()?
            .to_owned();
        Ok(format!(
            "Repeat({count_repr}, {tracks_repr}, line_names={names_repr})"
        ))
    }

    fn __eq__(&self, py: Python<'_>, other: &Repeat) -> PyResult<bool> {
        if self.count != other.count
            || self.line_names != other.line_names
            || self.tracks.len() != other.tracks.len()
        {
            return Ok(false);
        }
        for (a, b) in self.tracks.iter().zip(&other.tracks) {
            if !a.bind(py).eq(b.bind(py))? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn __hash__(&self, py: Python<'_>) -> PyResult<u64> {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        match self.count {
            taffy::RepetitionCount::AutoFill => 0u8.hash(&mut hasher),
            taffy::RepetitionCount::AutoFit => 1u8.hash(&mut hasher),
            taffy::RepetitionCount::Count(n) => {
                2u8.hash(&mut hasher);
                n.hash(&mut hasher);
            }
        }
        for track in &self.tracks {
            track.bind(py).hash()?.hash(&mut hasher);
        }
        self.line_names.hash(&mut hasher);
        Ok(hasher.finish())
    }
}

impl Repeat {
    pub(crate) fn to_taffy(&self, py: Python<'_>) -> taffy::GridTemplateRepetition<String> {
        taffy::GridTemplateRepetition {
            count: self.count,
            tracks: self
                .tracks
                .iter()
                .map(|t| {
                    let input: GridTrackInput = t
                        .bind(py)
                        .extract()
                        .expect("Repeat tracks validated at construction");
                    input.to_taffy(py)
                })
                .collect(),
            line_names: self.line_names.clone(),
        }
    }

    pub(crate) fn from_taffy(
        py: Python<'_>,
        repetition: &taffy::GridTemplateRepetition<String>,
    ) -> PyResult<Self> {
        Ok(Self {
            count: repetition.count,
            tracks: repetition
                .tracks
                .iter()
                .map(|t| grid_track_to_py(py, *t))
                .collect::<PyResult<_>>()?,
            line_names: repetition.line_names.clone(),
        })
    }
}

// ─── Grid placement only ──────────────────────────────────────────────────

/// A 1-based grid line index (negative indices count from the end).
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::Line`](https://docs.rs/taffy/0.15.0/taffy/style/enum.GridPlacement.html),
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
    pub fn new(index: i16) -> PyResult<Self> {
        if index == 0 {
            return Err(InvalidGridLine::new_err(
                "GridLine index must not be 0 (grid lines are 1-based; negative indices count from the end)",
            ));
        }
        Ok(Self { index })
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

    fn __hash__(&self) -> isize {
        self.index as isize
    }
}

/// Span a number of grid tracks.
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::Span`](https://docs.rs/taffy/0.15.0/taffy/style/enum.GridPlacement.html),
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
    pub fn new(count: u16) -> PyResult<Self> {
        if count == 0 {
            return Err(InvalidGridSpan::new_err(
                "GridSpan count must be at least 1",
            ));
        }
        Ok(Self { count })
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

    fn __hash__(&self) -> isize {
        self.count as isize
    }
}

/// Python `repr()` of a string, for building reprs that round-trip through `eval`.
fn str_repr(py: Python<'_>, s: &str) -> PyResult<String> {
    Ok(pyo3::types::PyString::new(py, s)
        .repr()?
        .to_str()?
        .to_owned())
}

/// Place at a grid line with the given name.
///
/// With no `index` (CSS `<custom-ident>`), a start line is the start edge of the grid area with
/// that name (the line named `name-start`) and an end line its end edge (`name-end`), falling
/// back to the first line named `name`. With an `index` (CSS `<integer> <custom-ident>`), place
/// at the `index`th line named `name`, counting from the end if negative; lines past the
/// explicit grid count as having every name.
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::NamedLine`](https://docs.rs/taffy/0.15.0/taffy/style/enum.GridPlacement.html),
/// [MDN `grid-row-start`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row-start)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct NamedGridLine {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub index: Option<i16>,
}

#[pymethods]
impl NamedGridLine {
    #[new]
    #[pyo3(signature = (name, index=None))]
    pub fn new(name: String, index: Option<i16>) -> PyResult<Self> {
        if index == Some(0) {
            return Err(InvalidGridLine::new_err(
                "NamedGridLine index must not be 0 (lines are counted from 1, or from -1 at the end)",
            ));
        }
        Ok(Self { name, index })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["name", "index"]).unwrap().unbind()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let name = str_repr(py, &self.name)?;
        Ok(match self.index {
            Some(index) => format!("NamedGridLine({name}, {index})"),
            None => format!("NamedGridLine({name})"),
        })
    }

    fn __eq__(&self, other: &NamedGridLine) -> bool {
        self == other
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.name.hash(&mut hasher);
        self.index.hash(&mut hasher);
        hasher.finish()
    }
}

/// Span until the `count`th grid line with the given name.
///
/// Used in grid placement (`GridPlacement.start`, `GridPlacement.end`).
///
/// See: [taffy `GridPlacement::NamedSpan`](https://docs.rs/taffy/0.15.0/taffy/style/enum.GridPlacement.html),
/// [MDN `grid-row-start` (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row-start)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct NamedGridSpan {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub count: u16,
}

#[pymethods]
impl NamedGridSpan {
    #[new]
    #[pyo3(signature = (name, count=1))]
    pub fn new(name: String, count: u16) -> PyResult<Self> {
        if count == 0 {
            return Err(InvalidGridSpan::new_err(
                "NamedGridSpan count must be at least 1",
            ));
        }
        Ok(Self { name, count })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["name", "count"]).unwrap().unbind()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!(
            "NamedGridSpan({}, {})",
            str_repr(py, &self.name)?,
            self.count
        ))
    }

    fn __eq__(&self, other: &NamedGridSpan) -> bool {
        self == other
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.name.hash(&mut hasher);
        self.count.hash(&mut hasher);
        hasher.finish()
    }
}

// ─── Grid placement ────────────────────────────────────────────────────────

pub(crate) fn hash_taffy_grid_placement<H: std::hash::Hasher>(
    gp: &TaffyGridPlacement,
    hasher: &mut H,
) {
    use std::hash::Hash;
    match gp {
        TaffyGridPlacement::Auto => 0u8.hash(hasher),
        TaffyGridPlacement::Line(gl) => {
            1u8.hash(hasher);
            gl.as_i16().hash(hasher);
        }
        TaffyGridPlacement::Span(n) => {
            2u8.hash(hasher);
            n.hash(hasher);
        }
        TaffyGridPlacement::NamedLine(s, i) => {
            3u8.hash(hasher);
            (s.as_ref() as &str).hash(hasher);
            i.hash(hasher);
        }
        TaffyGridPlacement::NamedSpan(s, n) => {
            4u8.hash(hasher);
            (s.as_ref() as &str).hash(hasher);
            n.hash(hasher);
        }
    }
}

pub(crate) fn hash_taffy_compact_length<H: std::hash::Hasher>(cl: CompactLength, hasher: &mut H) {
    use std::hash::Hash;
    cl.tag().hash(hasher);
    cl.value().to_bits().hash(hasher);
}

pub(crate) fn hash_taffy_track_sizing_function<H: std::hash::Hasher>(
    tsf: TrackSizingFunction,
    hasher: &mut H,
) {
    hash_taffy_compact_length(tsf.min.into_raw(), hasher);
    hash_taffy_compact_length(tsf.max.into_raw(), hasher);
}

pub(crate) fn hash_taffy_template_component<H: std::hash::Hasher>(
    comp: &taffy::GridTemplateComponent<String>,
    hasher: &mut H,
) {
    use std::hash::Hash;
    match comp {
        taffy::GridTemplateComponent::Single(tsf) => {
            0u8.hash(hasher);
            hash_taffy_track_sizing_function(*tsf, hasher);
        }
        taffy::GridTemplateComponent::Repeat(rep) => {
            1u8.hash(hasher);
            match rep.count {
                taffy::RepetitionCount::AutoFill => 0u8.hash(hasher),
                taffy::RepetitionCount::AutoFit => 1u8.hash(hasher),
                taffy::RepetitionCount::Count(n) => {
                    2u8.hash(hasher);
                    n.hash(hasher);
                }
            }
            rep.tracks.len().hash(hasher);
            for tsf in &rep.tracks {
                hash_taffy_track_sizing_function(*tsf, hasher);
            }
            rep.line_names.hash(hasher);
        }
    }
}

pub(crate) fn hash_taffy_template_area<H: std::hash::Hasher>(
    area: &taffy::GridTemplateArea<String>,
    hasher: &mut H,
) {
    use std::hash::Hash;
    area.name.hash(hasher);
    area.row_start.hash(hasher);
    area.row_end.hash(hasher);
    area.column_start.hash(hasher);
    area.column_end.hash(hasher);
}

/// A start/end pair of grid placements for a child item.
///
/// Each of `start` and `end` is a `GridLine | GridSpan | NamedGridLine | NamedGridSpan | Auto`
/// value. Defaults both to `Auto` (the CSS default for unplaced items).
///
/// See: [taffy `Line<GridPlacement>`](https://docs.rs/taffy/0.15.0/taffy/geometry/struct.Line.html),
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

    fn __eq__(&self, other: &GridPlacement) -> bool {
        self.start == other.start && self.end == other.end
    }

    fn __hash__(&self) -> u64 {
        use std::hash::Hasher;
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_taffy_grid_placement(&self.start, &mut hasher);
        hash_taffy_grid_placement(&self.end, &mut hasher);
        hasher.finish()
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

// ─── Grid template areas ───────────────────────────────────────────────────

/// A named rectangular area of a grid template, bounded by 1-based grid lines.
///
/// Raises [`InvalidGridTemplateArea`] if a start line is 0 or an end line is not after its
/// start line.
///
/// See: [taffy `GridTemplateArea`](https://docs.rs/taffy/0.15.0/taffy/style/struct.GridTemplateArea.html),
/// [MDN `grid-template-areas`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct GridTemplateArea {
    pub(crate) inner: taffy::GridTemplateArea<String>,
}

#[pymethods]
impl GridTemplateArea {
    #[new]
    pub fn new(
        name: String,
        row_start: u16,
        row_end: u16,
        column_start: u16,
        column_end: u16,
    ) -> PyResult<Self> {
        if row_start == 0 || column_start == 0 {
            return Err(InvalidGridTemplateArea::new_err(
                "GridTemplateArea start lines must be at least 1",
            ));
        }
        if row_end <= row_start || column_end <= column_start {
            return Err(InvalidGridTemplateArea::new_err(
                "GridTemplateArea end lines must be after their start lines",
            ));
        }
        Ok(Self {
            inner: taffy::GridTemplateArea {
                name,
                row_start,
                row_end,
                column_start,
                column_end,
            },
        })
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(
            py,
            ["name", "row_start", "row_end", "column_start", "column_end"],
        )
        .unwrap()
        .unbind()
    }

    #[getter]
    fn name(&self) -> String {
        self.inner.name.clone()
    }

    #[getter]
    fn row_start(&self) -> u16 {
        self.inner.row_start
    }

    #[getter]
    fn row_end(&self) -> u16 {
        self.inner.row_end
    }

    #[getter]
    fn column_start(&self) -> u16 {
        self.inner.column_start
    }

    #[getter]
    fn column_end(&self) -> u16 {
        self.inner.column_end
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let a = &self.inner;
        Ok(format!(
            "GridTemplateArea({}, {}, {}, {}, {})",
            str_repr(py, &a.name)?,
            a.row_start,
            a.row_end,
            a.column_start,
            a.column_end
        ))
    }

    fn __eq__(&self, other: &GridTemplateArea) -> bool {
        self == other
    }

    fn __hash__(&self) -> u64 {
        use std::hash::Hasher;
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        hash_taffy_template_area(&self.inner, &mut hasher);
        hasher.finish()
    }
}

/// A grid template's named areas, plus its size in tracks.
///
/// The template can be larger than the extent of its named areas (because of unnamed cells),
/// so `row_count` and `column_count` are stored explicitly. Build one from CSS
/// `grid-template-areas` strings with [`GridTemplateAreas.from_strings`].
///
/// Raises [`InvalidGridTemplateAreas`] if an area extends past `row_count` / `column_count`,
/// or if two areas share a name.
///
/// See: [taffy `GridTemplateAreas`](https://docs.rs/taffy/0.15.0/taffy/style/struct.GridTemplateAreas.html),
/// [MDN `grid-template-areas`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct GridTemplateAreas {
    pub(crate) inner: taffy::GridTemplateAreas<String>,
}

#[pymethods]
impl GridTemplateAreas {
    #[new]
    pub fn new(areas: Vec<GridTemplateArea>, row_count: u16, column_count: u16) -> PyResult<Self> {
        let mut names = std::collections::HashSet::new();
        for area in &areas {
            let a = &area.inner;
            if !names.insert(a.name.as_str()) {
                return Err(InvalidGridTemplateAreas::new_err(format!(
                    "GridTemplateAreas has more than one area named {:?}",
                    a.name
                )));
            }
            if a.row_end - 1 > row_count || a.column_end - 1 > column_count {
                return Err(InvalidGridTemplateAreas::new_err(format!(
                    "GridTemplateAreas area {:?} extends past the {row_count}x{column_count} template",
                    a.name
                )));
            }
        }
        Ok(Self {
            inner: taffy::GridTemplateAreas {
                areas: areas.into_iter().map(|a| a.inner).collect(),
                row_count,
                column_count,
            },
        })
    }

    /// Parse CSS `grid-template-areas` row strings, e.g. `["header header", "nav main"]`.
    #[staticmethod]
    fn from_strings(rows: Vec<String>) -> PyResult<Self> {
        parse_grid_template_areas(&rows)
            .map(|inner| Self { inner })
            .map_err(InvalidGridTemplateAreas::new_err)
    }

    #[classattr]
    fn __match_args__(py: Python<'_>) -> Py<PyTuple> {
        PyTuple::new(py, ["areas", "row_count", "column_count"])
            .unwrap()
            .unbind()
    }

    #[getter]
    fn areas(&self) -> Vec<GridTemplateArea> {
        self.inner
            .areas
            .iter()
            .map(|a| GridTemplateArea { inner: a.clone() })
            .collect()
    }

    #[getter]
    fn row_count(&self) -> u16 {
        self.inner.row_count
    }

    #[getter]
    fn column_count(&self) -> u16 {
        self.inner.column_count
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let areas_repr = pyo3::types::PyList::new(py, self.areas())?
            .repr()?
            .to_str()?
            .to_owned();
        Ok(format!(
            "GridTemplateAreas({areas_repr}, {}, {})",
            self.inner.row_count, self.inner.column_count
        ))
    }

    fn __eq__(&self, other: &GridTemplateAreas) -> bool {
        self == other
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        self.inner.row_count.hash(&mut hasher);
        self.inner.column_count.hash(&mut hasher);
        for area in &self.inner.areas {
            hash_taffy_template_area(area, &mut hasher);
        }
        hasher.finish()
    }
}

/// Split one `grid-template-areas` row into cells: `Some(name)` for a named cell, `None` for a
/// null cell (a run of one or more `.`).
///
/// Follows the CSS tokenization of the property: names are runs of identifier characters,
/// whitespace separates cells, and any other character makes the template invalid.
fn tokenize_grid_template_row(row: &str) -> Result<Vec<Option<&str>>, String> {
    fn is_name_char(c: char) -> bool {
        c.is_alphanumeric() || c == '-' || c == '_' || !c.is_ascii()
    }

    let mut cells = Vec::new();
    let mut rest = row;
    while let Some(c) = rest.chars().next() {
        if c.is_whitespace() {
            rest = &rest[c.len_utf8()..];
        } else if c == '.' {
            rest = rest.trim_start_matches('.');
            cells.push(None);
        } else if is_name_char(c) {
            let end = rest.find(|c: char| !is_name_char(c)).unwrap_or(rest.len());
            cells.push(Some(&rest[..end]));
            rest = &rest[end..];
        } else {
            return Err(format!(
                "grid template row {row:?} contains invalid character {c:?}"
            ));
        }
    }
    Ok(cells)
}

/// Parse CSS `grid-template-areas` row strings into taffy's representation, rejecting templates
/// CSS considers invalid (ragged rows, non-rectangular areas).
fn parse_grid_template_areas(rows: &[String]) -> Result<taffy::GridTemplateAreas<String>, String> {
    /// Track bounds (0-based, inclusive) and cell count of one area while scanning.
    struct Extent<'a> {
        name: &'a str,
        rows: (usize, usize),
        columns: (usize, usize),
        cells: usize,
    }

    if rows.is_empty() {
        return Err("grid template must have at least one row".to_owned());
    }
    let mut column_count = None;
    let mut extents: Vec<Extent> = Vec::new();
    for (r, row) in rows.iter().enumerate() {
        let cells = tokenize_grid_template_row(row)?;
        if cells.is_empty() {
            return Err(format!("grid template row {row:?} has no cells"));
        }
        let expected = *column_count.get_or_insert(cells.len());
        if cells.len() != expected {
            return Err(format!(
                "grid template rows must all have the same number of cells, but row {row:?} has {} instead of {expected}",
                cells.len()
            ));
        }
        for (c, name) in cells.into_iter().enumerate() {
            let Some(name) = name else { continue };
            match extents.iter_mut().find(|e| e.name == name) {
                Some(e) => {
                    e.rows = (e.rows.0.min(r), e.rows.1.max(r));
                    e.columns = (e.columns.0.min(c), e.columns.1.max(c));
                    e.cells += 1;
                }
                None => extents.push(Extent {
                    name,
                    rows: (r, r),
                    columns: (c, c),
                    cells: 1,
                }),
            }
        }
    }

    let to_line = |index: usize| {
        u16::try_from(index + 1).map_err(|_| "grid template is too large".to_owned())
    };
    let areas = extents
        .iter()
        .map(|e| {
            let height = e.rows.1 - e.rows.0 + 1;
            let width = e.columns.1 - e.columns.0 + 1;
            if e.cells != height * width {
                return Err(format!("grid area {:?} is not a rectangle", e.name));
            }
            Ok(taffy::GridTemplateArea {
                name: e.name.to_owned(),
                row_start: to_line(e.rows.0)?,
                row_end: to_line(e.rows.1 + 1)?,
                column_start: to_line(e.columns.0)?,
                column_end: to_line(e.columns.1 + 1)?,
            })
        })
        .collect::<Result<_, String>>()?;
    Ok(taffy::GridTemplateAreas {
        areas,
        row_count: to_line(rows.len() - 1)?,
        column_count: to_line(column_count.expect("rows is non-empty") - 1)?,
    })
}

// ─── Input enums (FromPyObject, not pyclasses) ─────────────────────────────

/// How an input enum's pyclass variant takes its value from an instance of `Class`.
trait ClassVariant {
    type Class: pyo3::PyClass + pyo3::PyTypeInfo;
    fn from_instance(instance: &Bound<'_, Self::Class>) -> Self;
}

/// Classes that hold Python objects (and so aren't `Clone`) are kept as a new reference.
impl<T: pyo3::PyClass + pyo3::PyTypeInfo> ClassVariant for Py<T> {
    type Class = T;
    fn from_instance(instance: &Bound<'_, T>) -> Self {
        instance.clone().unbind()
    }
}

/// Frozen classes holding plain Rust values are copied out of the instance.
macro_rules! cloned_class_variants {
    ($($class:ty),* $(,)?) => {$(
        impl ClassVariant for $class {
            type Class = $class;
            fn from_instance(instance: &Bound<'_, $class>) -> Self {
                instance.get().clone()
            }
        }
    )*};
}

cloned_class_variants!(
    Length,
    Percent,
    Auto,
    MinContent,
    MaxContent,
    Stretch,
    FitContentKeyword,
    Content,
    Definite,
    Fraction,
    AutoFill,
    AutoFit,
    GridLine,
    GridSpan,
    NamedGridLine,
    NamedGridSpan,
);

/// The Python type names an input accepts, for the error raised when none of them match.
trait AcceptedTypes {
    fn accepted_types(py: Python<'_>, names: &mut Vec<String>) -> PyResult<()>;
}

impl AcceptedTypes for u16 {
    fn accepted_types(_py: Python<'_>, names: &mut Vec<String>) -> PyResult<()> {
        names.push("int".to_owned());
        Ok(())
    }
}

/// The `TypeError` for an object that matches none of `T`'s accepted types.
fn input_type_error<T: AcceptedTypes>(obj: &Bound<'_, PyAny>) -> PyErr {
    let message = || -> PyResult<String> {
        let mut names = Vec::new();
        T::accepted_types(obj.py(), &mut names)?;
        Ok(format!(
            "expected {}, got {}",
            names.join(" | "),
            obj.get_type().name()?
        ))
    };
    match message() {
        Ok(message) => PyTypeError::new_err(message),
        Err(e) => e,
    }
}

/// Define an enum of the Python values a field accepts, and its `FromPyObject`.
///
/// `classes` variants match an instance of a pyclass; `nested` variants match whatever another
/// input type accepts. pyo3's derived `FromPyObject` builds a formatted `PyErr` for every variant
/// it tries and misses, which made extraction cost grow with a variant's position in the enum.
/// A `cast` that misses builds no error, so every pyclass variant costs the same; a nested
/// `extract` that misses does build one, so nested variants are tried last.
macro_rules! input_enum {
    (
        $(#[$meta:meta])*
        pub enum $name:ident {
            classes { $($class_variant:ident($class_ty:ty)),* $(,)? }
            $(nested { $($nested_variant:ident($nested_ty:ty)),* $(,)? })?
        }
    ) => {
        $(#[$meta])*
        pub enum $name {
            $($class_variant($class_ty),)*
            $($($nested_variant($nested_ty),)*)?
        }

        impl AcceptedTypes for $name {
            fn accepted_types(py: Python<'_>, names: &mut Vec<String>) -> PyResult<()> {
                $(
                    let class = <<$class_ty as ClassVariant>::Class as pyo3::PyTypeInfo>::type_object(py);
                    names.push(class.name()?.to_string());
                )*
                $($(<$nested_ty as AcceptedTypes>::accepted_types(py, names)?;)*)?
                Ok(())
            }
        }

        impl<'a, 'py> FromPyObject<'a, 'py> for $name {
            type Error = PyErr;

            fn extract(obj: pyo3::Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
                $(
                    if let Ok(instance) = obj.cast::<<$class_ty as ClassVariant>::Class>() {
                        return Ok(Self::$class_variant(<$class_ty as ClassVariant>::from_instance(
                            &instance,
                        )));
                    }
                )*
                $($(
                    match obj.extract::<$nested_ty>().map_err(Into::<PyErr>::into) {
                        Ok(value) => return Ok(Self::$nested_variant(value)),
                        // The nested input took the type but not the value (like a negative
                        // `int` for a `u16`), so its error says more than a list of types would.
                        Err(e) if !e.is_instance_of::<PyTypeError>(obj.py()) => return Err(e),
                        Err(_) => {}
                    }
                )*)?
                Err(input_type_error::<Self>(&obj))
            }
        }
    };
}

input_enum! {
    /// Accepts `Length | Percent | Auto | MinContent | MaxContent | FitContent | FitContentKeyword
    /// | Stretch` from Python (for `size_*`).
    pub enum DimensionInput {
        classes {
            Length(Length),
            Percent(Percent),
            Auto(Auto),
            MinContent(MinContent),
            MaxContent(MaxContent),
            FitContent(Py<FitContent>),
            FitContentKeyword(FitContentKeyword),
            Stretch(Stretch),
        }
    }
}

impl DimensionInput {
    pub fn to_taffy(&self, py: Python<'_>) -> taffy::Dimension {
        match self {
            DimensionInput::Length(l) => taffy::Dimension::length(l.value),
            DimensionInput::Percent(p) => taffy::Dimension::percent(p.value),
            DimensionInput::Auto(_) => taffy::Dimension::auto(),
            DimensionInput::MinContent(_) => taffy::Dimension::min_content(),
            DimensionInput::MaxContent(_) => taffy::Dimension::max_content(),
            DimensionInput::FitContent(fc) => fc.bind(py).borrow().to_taffy_dimension(py),
            DimensionInput::FitContentKeyword(_) => taffy::Dimension::fit_content(),
            DimensionInput::Stretch(_) => taffy::Dimension::stretch(),
        }
    }
}

input_enum! {
    /// Accepts everything [`DimensionInput`] does, plus `Content` (for `flex_basis`).
    pub enum FlexBasisInput {
        classes {
            Content(Content),
        }
        nested {
            Dimension(DimensionInput),
        }
    }
}

impl FlexBasisInput {
    pub fn to_taffy(&self, py: Python<'_>) -> taffy::Dimension {
        match self {
            FlexBasisInput::Content(_) => taffy::Dimension::content(),
            FlexBasisInput::Dimension(d) => d.to_taffy(py),
        }
    }
}

input_enum! {
    /// Accepts `Length | Percent` from Python.
    pub enum LengthPercentageInput {
        classes {
            Length(Length),
            Percent(Percent),
        }
    }
}

impl LengthPercentageInput {
    pub fn to_taffy(&self) -> taffy::LengthPercentage {
        match self {
            LengthPercentageInput::Length(l) => taffy::LengthPercentage::length(l.value),
            LengthPercentageInput::Percent(p) => taffy::LengthPercentage::percent(p.value),
        }
    }
}

input_enum! {
    /// Accepts `Length | Percent | Auto` from Python (for margin/inset fields).
    pub enum LengthPercentageAutoInput {
        classes {
            Length(Length),
            Percent(Percent),
            Auto(Auto),
        }
    }
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

input_enum! {
    /// Accepts `Definite | MinContent | MaxContent` from Python.
    pub enum AvailableSpaceInput {
        classes {
            Definite(Definite),
            MinContent(MinContent),
            MaxContent(MaxContent),
        }
    }
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

input_enum! {
    /// Accepts `Length | Percent | Auto | MinContent | MaxContent` — min side of minmax().
    pub enum GridTrackMinInput {
        classes {
            Length(Length),
            Percent(Percent),
            Auto(Auto),
            MinContent(MinContent),
            MaxContent(MaxContent),
        }
    }
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

input_enum! {
    /// Accepts `Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent` — max side of minmax().
    pub enum GridTrackMaxInput {
        classes {
            Length(Length),
            Percent(Percent),
            Auto(Auto),
            MinContent(MinContent),
            MaxContent(MaxContent),
            Fraction(Fraction),
            FitContent(Py<FitContent>),
        }
    }
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

input_enum! {
    /// Accepts the full set of grid track values from Python.
    pub enum GridTrackInput {
        classes {
            Length(Length),
            Percent(Percent),
            Auto(Auto),
            MinContent(MinContent),
            MaxContent(MaxContent),
            Fraction(Fraction),
            Minmax(Py<Minmax>),
            FitContent(Py<FitContent>),
        }
    }
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

input_enum! {
    /// Accepts a grid track value or a `Repeat` (for `grid_template_rows` / `grid_template_columns`).
    pub enum GridTemplateInput {
        classes {
            Repeat(Py<Repeat>),
        }
        nested {
            Track(GridTrackInput),
        }
    }
}

impl GridTemplateInput {
    pub fn to_taffy(&self, py: Python<'_>) -> taffy::GridTemplateComponent<String> {
        match self {
            GridTemplateInput::Repeat(r) => {
                taffy::GridTemplateComponent::Repeat(r.bind(py).borrow().to_taffy(py))
            }
            GridTemplateInput::Track(t) => taffy::GridTemplateComponent::Single(t.to_taffy(py)),
        }
    }
}

input_enum! {
    /// Accepts `GridLine | GridSpan | NamedGridLine | NamedGridSpan | Auto` for grid placement.
    pub enum GridPlacementInput {
        classes {
            GridLine(GridLine),
            GridSpan(GridSpan),
            NamedGridLine(NamedGridLine),
            NamedGridSpan(NamedGridSpan),
            Auto(Auto),
        }
    }
}

impl GridPlacementInput {
    pub fn to_taffy(&self) -> TaffyGridPlacement {
        match self {
            GridPlacementInput::GridLine(gl) => TaffyGridPlacement::from_line_index(gl.index),
            GridPlacementInput::GridSpan(gs) => TaffyGridPlacement::Span(gs.count),
            GridPlacementInput::NamedGridLine(nl) => {
                // taffy represents an absent index as 0, which NamedGridLine rejects.
                TaffyGridPlacement::NamedLine(nl.name.clone(), nl.index.unwrap_or(0))
            }
            GridPlacementInput::NamedGridSpan(ns) => {
                TaffyGridPlacement::NamedSpan(ns.name.clone(), ns.count)
            }
            GridPlacementInput::Auto(_) => TaffyGridPlacement::Auto,
        }
    }
}

input_enum! {
    /// Accepts `int | AutoFill | AutoFit` as a `Repeat` count.
    pub enum RepetitionCountInput {
        classes {
            AutoFill(AutoFill),
            AutoFit(AutoFit),
        }
        nested {
            Count(u16),
        }
    }
}

// ─── Thread safety ─────────────────────────────────────────────────────────

/// A taffy value holding no `calc()` lengths, which is what makes it `Send` and `Sync`.
///
/// taffy's `CompactLength` stores a `*const ()`, so nothing containing one is `Send` or `Sync`
/// (DioxusLabs/taffy#823). The pointer is a real pointer only in a `calc()` value, which waxy
/// never constructs (hence the `unreachable!`s converting taffy values to Python); every other
/// length packs plain bits into it. Nor does taffy dereference it: it hands a `calc()` pointer to
/// `LayoutPartialTree::resolve_calc_value`, which `taffy::TaffyTree` implements by ignoring it.
///
/// Wrapping just the taffy value, rather than declaring a whole pyclass `Send`, leaves the
/// compiler checking the pyclass's other fields.
#[derive(Clone, Debug, PartialEq)]
pub(crate) struct NoCalc<T>(pub(crate) T);

impl<T> std::ops::Deref for NoCalc<T> {
    type Target = T;

    fn deref(&self) -> &T {
        &self.0
    }
}

impl<T> std::ops::DerefMut for NoCalc<T> {
    fn deref_mut(&mut self) -> &mut T {
        &mut self.0
    }
}

// SAFETY: see `NoCalc`. These are per type rather than for every `T`, so wrapping some other
// non-`Send` type is still a compile error. On a taffy upgrade, delete them and `cargo check`:
// every complaint should trace back to `CompactLength`.
unsafe impl Send for NoCalc<taffy::Style> {}
unsafe impl Sync for NoCalc<taffy::Style> {}
unsafe impl Send for NoCalc<taffy::TaffyTree<Py<PyAny>>> {}
unsafe impl Sync for NoCalc<taffy::TaffyTree<Py<PyAny>>> {}

// ─── Taffy → Python conversion helpers ────────────────────────────────────
// These helpers bypass the `Length::new()` / `Percent::new()` constructors and
// construct `Length`/`Percent` directly from Taffy’s internal `CompactLength`
// representation. This is intentional: Taffy stores lengths/percentages internally
// without re-validating them. The only `Length`/`Percent` values that ever reach Taffy
// are ones we constructed via the validated constructors, so when we read back from
// Taffy we are only round-tripping previously-validated values, not accepting arbitrary
// unvalidated Taffy data.

/// Wrap a waxy value pyclass as an untyped Python object.
fn into_py_any<T: pyo3::PyClass + Into<pyo3::PyClassInitializer<T>>>(
    py: Python<'_>,
    value: T,
) -> PyResult<Py<PyAny>> {
    Ok(Py::new(py, value)?.into_any())
}

/// Build a `FitContent` whose limit is the given `Length` or `Percent`.
fn fit_content_to_py<T: pyo3::PyClass + Into<pyo3::PyClassInitializer<T>>>(
    py: Python<'_>,
    limit: T,
) -> PyResult<Py<PyAny>> {
    let limit = into_py_any(py, limit)?;
    into_py_any(py, FitContent { limit })
}

pub fn dimension_to_py(py: Python<'_>, d: taffy::Dimension) -> PyResult<Py<PyAny>> {
    use taffy::style::ExpandedDimension as E;
    match d.expand() {
        E::Length(value) => into_py_any(py, Length { value }),
        E::Percent(value) => into_py_any(py, Percent { value }),
        E::Auto => into_py_any(py, Auto {}),
        E::MinContent => into_py_any(py, MinContent {}),
        E::MaxContent => into_py_any(py, MaxContent {}),
        E::FitContentPx(value) => fit_content_to_py(py, Length { value }),
        E::FitContentPercent(value) => fit_content_to_py(py, Percent { value }),
        E::FitContent => into_py_any(py, FitContentKeyword {}),
        E::Stretch => into_py_any(py, Stretch {}),
        E::Content => into_py_any(py, Content {}),
        E::Calc(_) | E::FitContentCalc(_) => unreachable!("waxy never constructs calc() values"),
    }
}

pub fn length_percentage_to_py(py: Python<'_>, lp: taffy::LengthPercentage) -> PyResult<Py<PyAny>> {
    use taffy::style::ExpandedLengthPercentage as E;
    match lp.expand() {
        E::Length(value) => into_py_any(py, Length { value }),
        E::Percent(value) => into_py_any(py, Percent { value }),
        E::Calc(_) => unreachable!("waxy never constructs calc() values"),
    }
}

pub fn length_percentage_auto_to_py(
    py: Python<'_>,
    lpa: taffy::LengthPercentageAuto,
) -> PyResult<Py<PyAny>> {
    use taffy::style::ExpandedLengthPercentageAuto as E;
    match lpa.expand() {
        E::Length(value) => into_py_any(py, Length { value }),
        E::Percent(value) => into_py_any(py, Percent { value }),
        E::Auto => into_py_any(py, Auto {}),
        E::Calc(_) => unreachable!("waxy never constructs calc() values"),
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
    use taffy::style::ExpandedMinTrackSizingFunction as E;
    match min.expand() {
        E::Length(value) => into_py_any(py, Length { value }),
        E::Percent(value) => into_py_any(py, Percent { value }),
        E::Auto => into_py_any(py, Auto {}),
        E::MinContent => into_py_any(py, MinContent {}),
        E::MaxContent => into_py_any(py, MaxContent {}),
        E::Calc(_) => unreachable!("waxy never constructs calc() values"),
    }
}

fn grid_track_max_to_py(py: Python<'_>, max: MaxTrackSizingFunction) -> PyResult<Py<PyAny>> {
    use taffy::style::ExpandedMaxTrackSizingFunction as E;
    match max.expand() {
        E::Length(value) => into_py_any(py, Length { value }),
        E::Percent(value) => into_py_any(py, Percent { value }),
        E::Auto => into_py_any(py, Auto {}),
        E::MinContent => into_py_any(py, MinContent {}),
        E::MaxContent => into_py_any(py, MaxContent {}),
        E::FitContentPx(value) => fit_content_to_py(py, Length { value }),
        E::FitContentPercent(value) => fit_content_to_py(py, Percent { value }),
        E::Fr(value) => into_py_any(py, Fraction { value }),
        E::Calc(_) | E::FitContentCalc(_) => unreachable!("waxy never constructs calc() values"),
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
        TaffyGridPlacement::NamedLine(name, index) => {
            let index = (index != 0).then_some(index);
            into_py_any(py, NamedGridLine { name, index })
        }
        TaffyGridPlacement::NamedSpan(name, count) => {
            into_py_any(py, NamedGridSpan { name, count })
        }
    }
}

// ─── register ─────────────────────────────────────────────────────────────

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Length>()?;
    m.add_class::<Percent>()?;
    m.add_class::<Auto>()?;
    m.add_class::<MinContent>()?;
    m.add_class::<MaxContent>()?;
    m.add_class::<Stretch>()?;
    m.add_class::<FitContentKeyword>()?;
    m.add_class::<Content>()?;
    m.add_class::<Definite>()?;
    m.add_class::<Fraction>()?;
    m.add_class::<FitContent>()?;
    m.add_class::<Minmax>()?;
    m.add_class::<AutoFill>()?;
    m.add_class::<AutoFit>()?;
    m.add_class::<Repeat>()?;
    m.add_class::<GridLine>()?;
    m.add_class::<GridSpan>()?;
    m.add_class::<NamedGridLine>()?;
    m.add_class::<NamedGridSpan>()?;
    m.add_class::<GridPlacement>()?;
    m.add_class::<GridTemplateArea>()?;
    m.add_class::<GridTemplateAreas>()?;

    // Module-level singletons for common zero-field types
    m.add("AUTO", Py::new(m.py(), Auto {})?.into_any())?;
    m.add("MIN_CONTENT", Py::new(m.py(), MinContent {})?.into_any())?;
    m.add("MAX_CONTENT", Py::new(m.py(), MaxContent {})?.into_any())?;
    m.add("STRETCH", Py::new(m.py(), Stretch {})?.into_any())?;
    m.add(
        "FIT_CONTENT",
        Py::new(m.py(), FitContentKeyword {})?.into_any(),
    )?;
    m.add("CONTENT", Py::new(m.py(), Content {})?.into_any())?;
    m.add("AUTO_FILL", Py::new(m.py(), AutoFill {})?.into_any())?;
    m.add("AUTO_FIT", Py::new(m.py(), AutoFit {})?.into_any())?;

    Ok(())
}
