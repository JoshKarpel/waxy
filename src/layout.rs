use pyo3::prelude::*;

use pyo3::exceptions::PyIndexError;

use crate::enums::Direction;
use crate::geometry::{hash_f32, Line, Point, Rect, Size};
use crate::values::GridPlacement;

/// The computed layout of a node.
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Layout {
    inner: taffy::Layout,
}

#[pymethods]
impl Layout {
    fn __repr__(&self) -> String {
        format!(
            "Layout(location={}, size={})",
            Point::from(self.inner.location).__repr__(),
            Size::from(self.inner.size).__repr__()
        )
    }

    fn __eq__(&self, other: &Layout) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let l = &self.inner;
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        l.order.hash(&mut hasher);
        for v in [
            l.location.x,
            l.location.y,
            l.size.width,
            l.size.height,
            l.scrollable_overflow_rect.left,
            l.scrollable_overflow_rect.right,
            l.scrollable_overflow_rect.top,
            l.scrollable_overflow_rect.bottom,
            l.scrollbar_size.width,
            l.scrollbar_size.height,
            l.border.left,
            l.border.right,
            l.border.top,
            l.border.bottom,
            l.padding.left,
            l.padding.right,
            l.padding.top,
            l.padding.bottom,
            l.margin.left,
            l.margin.right,
            l.margin.top,
            l.margin.bottom,
        ] {
            hash_f32(v, &mut hasher);
        }
        hasher.finish()
    }

    #[getter]
    fn order(&self) -> u32 {
        self.inner.order
    }

    #[getter]
    fn location(&self) -> Point {
        self.inner.location.into()
    }

    #[getter]
    fn size(&self) -> Size {
        self.inner.size.into()
    }

    #[getter]
    fn scrollable_overflow_rect(&self) -> Rect {
        self.inner.scrollable_overflow_rect.into()
    }

    #[getter]
    fn scrollbar_size(&self) -> Size {
        self.inner.scrollbar_size.into()
    }

    #[getter]
    fn border(&self) -> Rect {
        self.inner.border.into()
    }

    #[getter]
    fn padding(&self) -> Rect {
        self.inner.padding.into()
    }

    #[getter]
    fn margin(&self) -> Rect {
        self.inner.margin.into()
    }

    fn content_box_width(&self) -> f32 {
        self.inner.content_box_width()
    }

    fn content_box_height(&self) -> f32 {
        self.inner.content_box_height()
    }

    fn content_box_size(&self) -> Size {
        self.inner.content_box_size().into()
    }

    fn content_box_x(&self) -> f32 {
        self.inner.content_box_x()
    }

    fn content_box_y(&self) -> f32 {
        self.inner.content_box_y()
    }

    fn scroll_width(&self) -> f32 {
        self.inner.scroll_width()
    }

    fn scroll_height(&self) -> f32 {
        self.inner.scroll_height()
    }
}

impl From<&taffy::Layout> for Layout {
    fn from(l: &taffy::Layout) -> Self {
        Self { inner: *l }
    }
}

/// The placement of one grid item, as 1-based grid line numbers.
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub struct DetailedGridItemInfo {
    #[pyo3(get)]
    pub row_start: u16,
    #[pyo3(get)]
    pub row_end: u16,
    #[pyo3(get)]
    pub column_start: u16,
    #[pyo3(get)]
    pub column_end: u16,
}

#[pymethods]
impl DetailedGridItemInfo {
    fn __repr__(&self) -> String {
        format!(
            "DetailedGridItemInfo(row_start={}, row_end={}, column_start={}, column_end={})",
            self.row_start, self.row_end, self.column_start, self.column_end
        )
    }

    fn __eq__(&self, other: &DetailedGridItemInfo) -> bool {
        self == other
    }

    fn __hash__(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        (
            self.row_start,
            self.row_end,
            self.column_start,
            self.column_end,
        )
            .hash(&mut hasher);
        hasher.finish()
    }
}

impl From<&taffy::DetailedGridItemsInfo> for DetailedGridItemInfo {
    fn from(item: &taffy::DetailedGridItemsInfo) -> Self {
        Self {
            row_start: item.row_start,
            row_end: item.row_end,
            column_start: item.column_start,
            column_end: item.column_end,
        }
    }
}

/// The computed tracks of one axis (rows or columns) of a grid container.
#[pyclass(frozen, skip_from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct DetailedGridTracksInfo {
    inner: taffy::DetailedGridTracksInfo,
}

#[pymethods]
impl DetailedGridTracksInfo {
    fn __repr__(&self) -> String {
        format!(
            "DetailedGridTracksInfo(negative_implicit_tracks={}, explicit_tracks={}, positive_implicit_tracks={})",
            self.inner.negative_implicit_tracks,
            self.inner.explicit_tracks,
            self.inner.positive_implicit_tracks
        )
    }

    fn __eq__(&self, other: &DetailedGridTracksInfo) -> bool {
        self.inner == other.inner
    }

    #[getter]
    fn negative_implicit_tracks(&self) -> u16 {
        self.inner.negative_implicit_tracks
    }

    #[getter]
    fn explicit_tracks(&self) -> u16 {
        self.inner.explicit_tracks
    }

    #[getter]
    fn positive_implicit_tracks(&self) -> u16 {
        self.inner.positive_implicit_tracks
    }

    #[getter]
    fn positions(&self) -> Vec<Line> {
        self.inner
            .positions
            .iter()
            .map(|&p| Line::from(p))
            .collect()
    }

    #[getter]
    fn line_names(&self) -> Vec<Vec<String>> {
        (0..=self.inner.positions.len())
            .map(|i| self.inner.names_for_line(i).to_vec())
            .collect()
    }

    fn names_for_line(&self, line_index: usize) -> Vec<String> {
        self.inner.names_for_line(line_index).to_vec()
    }
}

/// Detailed results of laying out a grid container: its tracks and item placements.
#[pyclass(frozen, skip_from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct DetailedGridInfo {
    inner: taffy::DetailedGridInfo,
}

#[pymethods]
impl DetailedGridInfo {
    fn __repr__(&self) -> String {
        format!(
            "DetailedGridInfo(rows={:?}, columns={:?}, items={})",
            self.inner.grid_template_rows(),
            self.inner.grid_template_columns(),
            self.inner.items.len()
        )
    }

    fn __eq__(&self, other: &DetailedGridInfo) -> bool {
        self.inner == other.inner
    }

    #[getter]
    fn rows(&self) -> DetailedGridTracksInfo {
        DetailedGridTracksInfo {
            inner: self.inner.rows.clone(),
        }
    }

    #[getter]
    fn columns(&self) -> DetailedGridTracksInfo {
        DetailedGridTracksInfo {
            inner: self.inner.columns.clone(),
        }
    }

    #[getter]
    fn items(&self) -> Vec<DetailedGridItemInfo> {
        self.inner
            .items
            .iter()
            .map(DetailedGridItemInfo::from)
            .collect()
    }

    fn grid_template_rows(&self) -> String {
        self.inner.grid_template_rows()
    }

    fn grid_template_columns(&self) -> String {
        self.inner.grid_template_columns()
    }

    fn item_grid_area(&self, item_index: usize) -> PyResult<(Point, Size)> {
        self.inner
            .item_grid_area(item_index)
            .map(|(location, size)| (location.into(), size.into()))
            .ok_or_else(|| {
                PyIndexError::new_err(format!(
                    "grid item index {item_index} out of range for {} items",
                    self.inner.items.len()
                ))
            })
    }

    fn resolve_absolute_grid_area(
        &self,
        grid_row: &GridPlacement,
        grid_column: &GridPlacement,
        direction: Direction,
        padding_box: &Rect,
    ) -> Rect {
        self.inner
            .resolve_absolute_grid_area(
                grid_row.into(),
                grid_column.into(),
                (&direction).into(),
                padding_box.into(),
            )
            .into()
    }
}

impl DetailedGridInfo {
    /// The grid info of a node, or `None` if it isn't a grid container (or hasn't been laid out).
    pub(crate) fn from_taffy(info: &taffy::DetailedLayoutInfo) -> Option<Self> {
        match info {
            taffy::DetailedLayoutInfo::Grid(grid) => Some(Self {
                inner: (**grid).clone(),
            }),
            taffy::DetailedLayoutInfo::None => None,
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Layout>()?;
    m.add_class::<DetailedGridInfo>()?;
    m.add_class::<DetailedGridTracksInfo>()?;
    m.add_class::<DetailedGridItemInfo>()?;
    Ok(())
}
