use pyo3::prelude::*;

use crate::dimensions::{Dimension, LengthPercentage, LengthPercentageAuto};
use crate::enums::{
    AlignContent, AlignItems, BoxSizing, Display, FlexDirection, FlexWrap, GridAutoFlow, Overflow,
    Position, TextAlign,
};
use crate::grid::{GridLine, GridTrack};

/// Style properties for a layout node.
#[pyclass(unsendable)]
#[derive(Clone, Debug)]
pub struct Style {
    pub(crate) inner: taffy::Style,
}

impl Style {
    pub(crate) fn to_taffy(&self) -> taffy::Style {
        self.inner.clone()
    }
}

// Helper to convert Option<AlignItems> to/from taffy
fn opt_align_items_to_taffy(v: &Option<AlignItems>) -> Option<taffy::AlignItems> {
    v.as_ref().map(|a| a.into())
}

fn opt_align_items_from_taffy(v: Option<taffy::AlignItems>) -> Option<AlignItems> {
    v.map(|a| a.into())
}

fn opt_align_content_to_taffy(v: &Option<AlignContent>) -> Option<taffy::AlignContent> {
    v.as_ref().map(|a| a.into())
}

fn opt_align_content_from_taffy(v: Option<taffy::AlignContent>) -> Option<AlignContent> {
    v.map(|a| a.into())
}

fn tracks_to_taffy(tracks: &[GridTrack]) -> Vec<taffy::style::GridTemplateComponent<String>> {
    tracks
        .iter()
        .map(|t| taffy::style::GridTemplateComponent::Single(t.inner))
        .collect()
}

fn tracks_from_taffy(tracks: &[taffy::style::GridTemplateComponent<String>]) -> Vec<GridTrack> {
    tracks
        .iter()
        .filter_map(|t| match t {
            taffy::style::GridTemplateComponent::Single(tsf) => Some(GridTrack { inner: *tsf }),
            _ => None, // Skip repeat() for now
        })
        .collect()
}

fn auto_tracks_to_taffy(tracks: &[GridTrack]) -> Vec<taffy::style::TrackSizingFunction> {
    tracks.iter().map(|t| t.inner).collect()
}

fn auto_tracks_from_taffy(tracks: &[taffy::style::TrackSizingFunction]) -> Vec<GridTrack> {
    tracks.iter().map(|t| GridTrack { inner: *t }).collect()
}

#[pymethods]
impl Style {
    #[new]
    #[pyo3(signature = (
        display = None,
        box_sizing = None,
        overflow_x = None,
        overflow_y = None,
        scrollbar_width = None,
        position = None,
        inset_left = None,
        inset_right = None,
        inset_top = None,
        inset_bottom = None,
        size_width = None,
        size_height = None,
        min_size_width = None,
        min_size_height = None,
        max_size_width = None,
        max_size_height = None,
        aspect_ratio = None,
        margin_left = None,
        margin_right = None,
        margin_top = None,
        margin_bottom = None,
        padding_left = None,
        padding_right = None,
        padding_top = None,
        padding_bottom = None,
        border_left = None,
        border_right = None,
        border_top = None,
        border_bottom = None,
        align_items = None,
        align_self = None,
        justify_items = None,
        justify_self = None,
        align_content = None,
        justify_content = None,
        gap_width = None,
        gap_height = None,
        text_align = None,
        flex_direction = None,
        flex_wrap = None,
        flex_basis = None,
        flex_grow = None,
        flex_shrink = None,
        grid_template_rows = None,
        grid_template_columns = None,
        grid_auto_rows = None,
        grid_auto_columns = None,
        grid_auto_flow = None,
        grid_row = None,
        grid_column = None,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        display: Option<Display>,
        box_sizing: Option<BoxSizing>,
        overflow_x: Option<Overflow>,
        overflow_y: Option<Overflow>,
        scrollbar_width: Option<f32>,
        position: Option<Position>,
        inset_left: Option<LengthPercentageAuto>,
        inset_right: Option<LengthPercentageAuto>,
        inset_top: Option<LengthPercentageAuto>,
        inset_bottom: Option<LengthPercentageAuto>,
        size_width: Option<Dimension>,
        size_height: Option<Dimension>,
        min_size_width: Option<Dimension>,
        min_size_height: Option<Dimension>,
        max_size_width: Option<Dimension>,
        max_size_height: Option<Dimension>,
        aspect_ratio: Option<f32>,
        margin_left: Option<LengthPercentageAuto>,
        margin_right: Option<LengthPercentageAuto>,
        margin_top: Option<LengthPercentageAuto>,
        margin_bottom: Option<LengthPercentageAuto>,
        padding_left: Option<LengthPercentage>,
        padding_right: Option<LengthPercentage>,
        padding_top: Option<LengthPercentage>,
        padding_bottom: Option<LengthPercentage>,
        border_left: Option<LengthPercentage>,
        border_right: Option<LengthPercentage>,
        border_top: Option<LengthPercentage>,
        border_bottom: Option<LengthPercentage>,
        align_items: Option<AlignItems>,
        align_self: Option<AlignItems>,
        justify_items: Option<AlignItems>,
        justify_self: Option<AlignItems>,
        align_content: Option<AlignContent>,
        justify_content: Option<AlignContent>,
        gap_width: Option<LengthPercentage>,
        gap_height: Option<LengthPercentage>,
        text_align: Option<TextAlign>,
        flex_direction: Option<FlexDirection>,
        flex_wrap: Option<FlexWrap>,
        flex_basis: Option<Dimension>,
        flex_grow: Option<f32>,
        flex_shrink: Option<f32>,
        grid_template_rows: Option<Vec<GridTrack>>,
        grid_template_columns: Option<Vec<GridTrack>>,
        grid_auto_rows: Option<Vec<GridTrack>>,
        grid_auto_columns: Option<Vec<GridTrack>>,
        grid_auto_flow: Option<GridAutoFlow>,
        grid_row: Option<GridLine>,
        grid_column: Option<GridLine>,
    ) -> Self {
        let mut style = taffy::Style::DEFAULT;

        if let Some(v) = display {
            style.display = (&v).into();
        }
        if let Some(v) = box_sizing {
            style.box_sizing = (&v).into();
        }
        if let Some(v) = overflow_x {
            style.overflow.x = (&v).into();
        }
        if let Some(v) = overflow_y {
            style.overflow.y = (&v).into();
        }
        if let Some(v) = scrollbar_width {
            style.scrollbar_width = v;
        }
        if let Some(v) = position {
            style.position = (&v).into();
        }

        // Inset
        if let Some(v) = inset_left {
            style.inset.left = (&v).into();
        }
        if let Some(v) = inset_right {
            style.inset.right = (&v).into();
        }
        if let Some(v) = inset_top {
            style.inset.top = (&v).into();
        }
        if let Some(v) = inset_bottom {
            style.inset.bottom = (&v).into();
        }

        // Size
        if let Some(v) = size_width {
            style.size.width = (&v).into();
        }
        if let Some(v) = size_height {
            style.size.height = (&v).into();
        }
        if let Some(v) = min_size_width {
            style.min_size.width = (&v).into();
        }
        if let Some(v) = min_size_height {
            style.min_size.height = (&v).into();
        }
        if let Some(v) = max_size_width {
            style.max_size.width = (&v).into();
        }
        if let Some(v) = max_size_height {
            style.max_size.height = (&v).into();
        }
        style.aspect_ratio = aspect_ratio;

        // Margin
        if let Some(v) = margin_left {
            style.margin.left = (&v).into();
        }
        if let Some(v) = margin_right {
            style.margin.right = (&v).into();
        }
        if let Some(v) = margin_top {
            style.margin.top = (&v).into();
        }
        if let Some(v) = margin_bottom {
            style.margin.bottom = (&v).into();
        }

        // Padding
        if let Some(v) = padding_left {
            style.padding.left = (&v).into();
        }
        if let Some(v) = padding_right {
            style.padding.right = (&v).into();
        }
        if let Some(v) = padding_top {
            style.padding.top = (&v).into();
        }
        if let Some(v) = padding_bottom {
            style.padding.bottom = (&v).into();
        }

        // Border
        if let Some(v) = border_left {
            style.border.left = (&v).into();
        }
        if let Some(v) = border_right {
            style.border.right = (&v).into();
        }
        if let Some(v) = border_top {
            style.border.top = (&v).into();
        }
        if let Some(v) = border_bottom {
            style.border.bottom = (&v).into();
        }

        // Alignment
        if let Some(v) = align_items {
            style.align_items = Some((&v).into());
        }
        if let Some(v) = align_self {
            style.align_self = Some((&v).into());
        }
        if let Some(v) = justify_items {
            style.justify_items = Some((&v).into());
        }
        if let Some(v) = justify_self {
            style.justify_self = Some((&v).into());
        }
        if let Some(v) = align_content {
            style.align_content = Some((&v).into());
        }
        if let Some(v) = justify_content {
            style.justify_content = Some((&v).into());
        }

        // Gap
        if let Some(v) = gap_width {
            style.gap.width = (&v).into();
        }
        if let Some(v) = gap_height {
            style.gap.height = (&v).into();
        }

        // Block
        if let Some(v) = text_align {
            style.text_align = (&v).into();
        }

        // Flexbox
        if let Some(v) = flex_direction {
            style.flex_direction = (&v).into();
        }
        if let Some(v) = flex_wrap {
            style.flex_wrap = (&v).into();
        }
        if let Some(v) = flex_basis {
            style.flex_basis = (&v).into();
        }
        if let Some(v) = flex_grow {
            style.flex_grow = v;
        }
        if let Some(v) = flex_shrink {
            style.flex_shrink = v;
        }

        // Grid
        if let Some(v) = grid_template_rows {
            style.grid_template_rows = tracks_to_taffy(&v);
        }
        if let Some(v) = grid_template_columns {
            style.grid_template_columns = tracks_to_taffy(&v);
        }
        if let Some(v) = grid_auto_rows {
            style.grid_auto_rows = auto_tracks_to_taffy(&v);
        }
        if let Some(v) = grid_auto_columns {
            style.grid_auto_columns = auto_tracks_to_taffy(&v);
        }
        if let Some(v) = grid_auto_flow {
            style.grid_auto_flow = (&v).into();
        }
        if let Some(v) = grid_row {
            style.grid_row = (&v).into();
        }
        if let Some(v) = grid_column {
            style.grid_column = (&v).into();
        }

        Self { inner: style }
    }

    // --- Getters and Setters ---

    #[getter]
    fn get_display(&self) -> Display {
        self.inner.display.into()
    }
    #[setter]
    fn set_display(&mut self, value: Display) {
        self.inner.display = (&value).into();
    }

    #[getter]
    fn get_box_sizing(&self) -> BoxSizing {
        self.inner.box_sizing.into()
    }
    #[setter]
    fn set_box_sizing(&mut self, value: BoxSizing) {
        self.inner.box_sizing = (&value).into();
    }

    #[getter]
    fn get_overflow_x(&self) -> Overflow {
        self.inner.overflow.x.into()
    }
    #[setter]
    fn set_overflow_x(&mut self, value: Overflow) {
        self.inner.overflow.x = (&value).into();
    }

    #[getter]
    fn get_overflow_y(&self) -> Overflow {
        self.inner.overflow.y.into()
    }
    #[setter]
    fn set_overflow_y(&mut self, value: Overflow) {
        self.inner.overflow.y = (&value).into();
    }

    #[getter]
    fn get_scrollbar_width(&self) -> f32 {
        self.inner.scrollbar_width
    }
    #[setter]
    fn set_scrollbar_width(&mut self, value: f32) {
        self.inner.scrollbar_width = value;
    }

    #[getter]
    fn get_position(&self) -> Position {
        self.inner.position.into()
    }
    #[setter]
    fn set_position(&mut self, value: Position) {
        self.inner.position = (&value).into();
    }

    // Inset
    #[getter]
    fn get_inset_left(&self) -> LengthPercentageAuto {
        self.inner.inset.left.into()
    }
    #[setter]
    fn set_inset_left(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.left = (&value).into();
    }
    #[getter]
    fn get_inset_right(&self) -> LengthPercentageAuto {
        self.inner.inset.right.into()
    }
    #[setter]
    fn set_inset_right(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.right = (&value).into();
    }
    #[getter]
    fn get_inset_top(&self) -> LengthPercentageAuto {
        self.inner.inset.top.into()
    }
    #[setter]
    fn set_inset_top(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.top = (&value).into();
    }
    #[getter]
    fn get_inset_bottom(&self) -> LengthPercentageAuto {
        self.inner.inset.bottom.into()
    }
    #[setter]
    fn set_inset_bottom(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.bottom = (&value).into();
    }

    // Size
    #[getter]
    fn get_size_width(&self) -> Dimension {
        self.inner.size.width.into()
    }
    #[setter]
    fn set_size_width(&mut self, value: Dimension) {
        self.inner.size.width = (&value).into();
    }
    #[getter]
    fn get_size_height(&self) -> Dimension {
        self.inner.size.height.into()
    }
    #[setter]
    fn set_size_height(&mut self, value: Dimension) {
        self.inner.size.height = (&value).into();
    }
    #[getter]
    fn get_min_size_width(&self) -> Dimension {
        self.inner.min_size.width.into()
    }
    #[setter]
    fn set_min_size_width(&mut self, value: Dimension) {
        self.inner.min_size.width = (&value).into();
    }
    #[getter]
    fn get_min_size_height(&self) -> Dimension {
        self.inner.min_size.height.into()
    }
    #[setter]
    fn set_min_size_height(&mut self, value: Dimension) {
        self.inner.min_size.height = (&value).into();
    }
    #[getter]
    fn get_max_size_width(&self) -> Dimension {
        self.inner.max_size.width.into()
    }
    #[setter]
    fn set_max_size_width(&mut self, value: Dimension) {
        self.inner.max_size.width = (&value).into();
    }
    #[getter]
    fn get_max_size_height(&self) -> Dimension {
        self.inner.max_size.height.into()
    }
    #[setter]
    fn set_max_size_height(&mut self, value: Dimension) {
        self.inner.max_size.height = (&value).into();
    }

    #[getter]
    fn get_aspect_ratio(&self) -> Option<f32> {
        self.inner.aspect_ratio
    }
    #[setter]
    fn set_aspect_ratio(&mut self, value: Option<f32>) {
        self.inner.aspect_ratio = value;
    }

    // Margin
    #[getter]
    fn get_margin_left(&self) -> LengthPercentageAuto {
        self.inner.margin.left.into()
    }
    #[setter]
    fn set_margin_left(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.left = (&value).into();
    }
    #[getter]
    fn get_margin_right(&self) -> LengthPercentageAuto {
        self.inner.margin.right.into()
    }
    #[setter]
    fn set_margin_right(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.right = (&value).into();
    }
    #[getter]
    fn get_margin_top(&self) -> LengthPercentageAuto {
        self.inner.margin.top.into()
    }
    #[setter]
    fn set_margin_top(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.top = (&value).into();
    }
    #[getter]
    fn get_margin_bottom(&self) -> LengthPercentageAuto {
        self.inner.margin.bottom.into()
    }
    #[setter]
    fn set_margin_bottom(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.bottom = (&value).into();
    }

    // Padding
    #[getter]
    fn get_padding_left(&self) -> LengthPercentage {
        self.inner.padding.left.into()
    }
    #[setter]
    fn set_padding_left(&mut self, value: LengthPercentage) {
        self.inner.padding.left = (&value).into();
    }
    #[getter]
    fn get_padding_right(&self) -> LengthPercentage {
        self.inner.padding.right.into()
    }
    #[setter]
    fn set_padding_right(&mut self, value: LengthPercentage) {
        self.inner.padding.right = (&value).into();
    }
    #[getter]
    fn get_padding_top(&self) -> LengthPercentage {
        self.inner.padding.top.into()
    }
    #[setter]
    fn set_padding_top(&mut self, value: LengthPercentage) {
        self.inner.padding.top = (&value).into();
    }
    #[getter]
    fn get_padding_bottom(&self) -> LengthPercentage {
        self.inner.padding.bottom.into()
    }
    #[setter]
    fn set_padding_bottom(&mut self, value: LengthPercentage) {
        self.inner.padding.bottom = (&value).into();
    }

    // Border
    #[getter]
    fn get_border_left(&self) -> LengthPercentage {
        self.inner.border.left.into()
    }
    #[setter]
    fn set_border_left(&mut self, value: LengthPercentage) {
        self.inner.border.left = (&value).into();
    }
    #[getter]
    fn get_border_right(&self) -> LengthPercentage {
        self.inner.border.right.into()
    }
    #[setter]
    fn set_border_right(&mut self, value: LengthPercentage) {
        self.inner.border.right = (&value).into();
    }
    #[getter]
    fn get_border_top(&self) -> LengthPercentage {
        self.inner.border.top.into()
    }
    #[setter]
    fn set_border_top(&mut self, value: LengthPercentage) {
        self.inner.border.top = (&value).into();
    }
    #[getter]
    fn get_border_bottom(&self) -> LengthPercentage {
        self.inner.border.bottom.into()
    }
    #[setter]
    fn set_border_bottom(&mut self, value: LengthPercentage) {
        self.inner.border.bottom = (&value).into();
    }

    // Alignment
    #[getter]
    fn get_align_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_items)
    }
    #[setter]
    fn set_align_items(&mut self, value: Option<AlignItems>) {
        self.inner.align_items = opt_align_items_to_taffy(&value);
    }

    #[getter]
    fn get_align_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_self)
    }
    #[setter]
    fn set_align_self(&mut self, value: Option<AlignItems>) {
        self.inner.align_self = opt_align_items_to_taffy(&value);
    }

    #[getter]
    fn get_justify_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_items)
    }
    #[setter]
    fn set_justify_items(&mut self, value: Option<AlignItems>) {
        self.inner.justify_items = opt_align_items_to_taffy(&value);
    }

    #[getter]
    fn get_justify_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_self)
    }
    #[setter]
    fn set_justify_self(&mut self, value: Option<AlignItems>) {
        self.inner.justify_self = opt_align_items_to_taffy(&value);
    }

    #[getter]
    fn get_align_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.align_content)
    }
    #[setter]
    fn set_align_content(&mut self, value: Option<AlignContent>) {
        self.inner.align_content = opt_align_content_to_taffy(&value);
    }

    #[getter]
    fn get_justify_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.justify_content)
    }
    #[setter]
    fn set_justify_content(&mut self, value: Option<AlignContent>) {
        self.inner.justify_content = opt_align_content_to_taffy(&value);
    }

    // Gap
    #[getter]
    fn get_gap_width(&self) -> LengthPercentage {
        self.inner.gap.width.into()
    }
    #[setter]
    fn set_gap_width(&mut self, value: LengthPercentage) {
        self.inner.gap.width = (&value).into();
    }
    #[getter]
    fn get_gap_height(&self) -> LengthPercentage {
        self.inner.gap.height.into()
    }
    #[setter]
    fn set_gap_height(&mut self, value: LengthPercentage) {
        self.inner.gap.height = (&value).into();
    }

    // Block
    #[getter]
    fn get_text_align(&self) -> TextAlign {
        self.inner.text_align.into()
    }
    #[setter]
    fn set_text_align(&mut self, value: TextAlign) {
        self.inner.text_align = (&value).into();
    }

    // Flexbox
    #[getter]
    fn get_flex_direction(&self) -> FlexDirection {
        self.inner.flex_direction.into()
    }
    #[setter]
    fn set_flex_direction(&mut self, value: FlexDirection) {
        self.inner.flex_direction = (&value).into();
    }

    #[getter]
    fn get_flex_wrap(&self) -> FlexWrap {
        self.inner.flex_wrap.into()
    }
    #[setter]
    fn set_flex_wrap(&mut self, value: FlexWrap) {
        self.inner.flex_wrap = (&value).into();
    }

    #[getter]
    fn get_flex_basis(&self) -> Dimension {
        self.inner.flex_basis.into()
    }
    #[setter]
    fn set_flex_basis(&mut self, value: Dimension) {
        self.inner.flex_basis = (&value).into();
    }

    #[getter]
    fn get_flex_grow(&self) -> f32 {
        self.inner.flex_grow
    }
    #[setter]
    fn set_flex_grow(&mut self, value: f32) {
        self.inner.flex_grow = value;
    }

    #[getter]
    fn get_flex_shrink(&self) -> f32 {
        self.inner.flex_shrink
    }
    #[setter]
    fn set_flex_shrink(&mut self, value: f32) {
        self.inner.flex_shrink = value;
    }

    // Grid
    #[getter]
    fn get_grid_template_rows(&self) -> Vec<GridTrack> {
        tracks_from_taffy(&self.inner.grid_template_rows)
    }
    #[setter]
    fn set_grid_template_rows(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_template_rows = tracks_to_taffy(&value);
    }

    #[getter]
    fn get_grid_template_columns(&self) -> Vec<GridTrack> {
        tracks_from_taffy(&self.inner.grid_template_columns)
    }
    #[setter]
    fn set_grid_template_columns(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_template_columns = tracks_to_taffy(&value);
    }

    #[getter]
    fn get_grid_auto_rows(&self) -> Vec<GridTrack> {
        auto_tracks_from_taffy(&self.inner.grid_auto_rows)
    }
    #[setter]
    fn set_grid_auto_rows(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_auto_rows = auto_tracks_to_taffy(&value);
    }

    #[getter]
    fn get_grid_auto_columns(&self) -> Vec<GridTrack> {
        auto_tracks_from_taffy(&self.inner.grid_auto_columns)
    }
    #[setter]
    fn set_grid_auto_columns(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_auto_columns = auto_tracks_to_taffy(&value);
    }

    #[getter]
    fn get_grid_auto_flow(&self) -> GridAutoFlow {
        self.inner.grid_auto_flow.into()
    }
    #[setter]
    fn set_grid_auto_flow(&mut self, value: GridAutoFlow) {
        self.inner.grid_auto_flow = (&value).into();
    }

    #[getter]
    fn get_grid_row(&self) -> GridLine {
        self.inner.grid_row.clone().into()
    }
    #[setter]
    fn set_grid_row(&mut self, value: GridLine) {
        self.inner.grid_row = (&value).into();
    }

    #[getter]
    fn get_grid_column(&self) -> GridLine {
        self.inner.grid_column.clone().into()
    }
    #[setter]
    fn set_grid_column(&mut self, value: GridLine) {
        self.inner.grid_column = (&value).into();
    }

    fn __repr__(&self) -> String {
        format!(
            "Style(display={:?}, position={:?})",
            self.inner.display, self.inner.position
        )
    }
}

impl From<&taffy::Style> for Style {
    fn from(s: &taffy::Style) -> Self {
        Self { inner: s.clone() }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Style>()?;
    Ok(())
}
