use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::dimensions::{Dimension, LengthPercentage, LengthPercentageAuto};
use crate::enums::{
    AlignContent, AlignItems, BoxSizing, Display, FlexDirection, FlexWrap, GridAutoFlow, Overflow,
    Position, TextAlign,
};
use crate::grid::{GridLine, GridTrack};

// Bit positions for tracking which fields are explicitly set.
const F_DISPLAY: u64 = 1 << 0;
const F_BOX_SIZING: u64 = 1 << 1;
const F_OVERFLOW_X: u64 = 1 << 2;
const F_OVERFLOW_Y: u64 = 1 << 3;
const F_SCROLLBAR_WIDTH: u64 = 1 << 4;
const F_POSITION: u64 = 1 << 5;
const F_INSET_LEFT: u64 = 1 << 6;
const F_INSET_RIGHT: u64 = 1 << 7;
const F_INSET_TOP: u64 = 1 << 8;
const F_INSET_BOTTOM: u64 = 1 << 9;
const F_SIZE_WIDTH: u64 = 1 << 10;
const F_SIZE_HEIGHT: u64 = 1 << 11;
const F_MIN_SIZE_WIDTH: u64 = 1 << 12;
const F_MIN_SIZE_HEIGHT: u64 = 1 << 13;
const F_MAX_SIZE_WIDTH: u64 = 1 << 14;
const F_MAX_SIZE_HEIGHT: u64 = 1 << 15;
const F_ASPECT_RATIO: u64 = 1 << 16;
const F_MARGIN_LEFT: u64 = 1 << 17;
const F_MARGIN_RIGHT: u64 = 1 << 18;
const F_MARGIN_TOP: u64 = 1 << 19;
const F_MARGIN_BOTTOM: u64 = 1 << 20;
const F_PADDING_LEFT: u64 = 1 << 21;
const F_PADDING_RIGHT: u64 = 1 << 22;
const F_PADDING_TOP: u64 = 1 << 23;
const F_PADDING_BOTTOM: u64 = 1 << 24;
const F_BORDER_LEFT: u64 = 1 << 25;
const F_BORDER_RIGHT: u64 = 1 << 26;
const F_BORDER_TOP: u64 = 1 << 27;
const F_BORDER_BOTTOM: u64 = 1 << 28;
const F_ALIGN_ITEMS: u64 = 1 << 29;
const F_ALIGN_SELF: u64 = 1 << 30;
const F_JUSTIFY_ITEMS: u64 = 1 << 31;
const F_JUSTIFY_SELF: u64 = 1 << 32;
const F_ALIGN_CONTENT: u64 = 1 << 33;
const F_JUSTIFY_CONTENT: u64 = 1 << 34;
const F_GAP_WIDTH: u64 = 1 << 35;
const F_GAP_HEIGHT: u64 = 1 << 36;
const F_TEXT_ALIGN: u64 = 1 << 37;
const F_FLEX_DIRECTION: u64 = 1 << 38;
const F_FLEX_WRAP: u64 = 1 << 39;
const F_FLEX_BASIS: u64 = 1 << 40;
const F_FLEX_GROW: u64 = 1 << 41;
const F_FLEX_SHRINK: u64 = 1 << 42;
const F_GRID_TEMPLATE_ROWS: u64 = 1 << 43;
const F_GRID_TEMPLATE_COLUMNS: u64 = 1 << 44;
const F_GRID_AUTO_ROWS: u64 = 1 << 45;
const F_GRID_AUTO_COLUMNS: u64 = 1 << 46;
const F_GRID_AUTO_FLOW: u64 = 1 << 47;
const F_GRID_ROW: u64 = 1 << 48;
const F_GRID_COLUMN: u64 = 1 << 49;

/// Style properties for a layout node.
#[pyclass(unsendable, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Style {
    pub(crate) inner: taffy::Style,
    /// Bitmask tracking which fields have been explicitly set.
    set_fields: u64,
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
    #[pyo3(signature = (**kwargs))]
    fn new(kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut style = taffy::Style::DEFAULT;
        let mut set_fields: u64 = 0;

        let Some(kwargs) = kwargs else {
            return Ok(Self {
                inner: style,
                set_fields,
            });
        };

        /// Extract a required (non-None) value for a field, or return a TypeError.
        macro_rules! set_field {
            ($key:literal, $flag:expr, $body:expr) => {
                if let Some(py_val) = kwargs.get_item($key)? {
                    if py_val.is_none() {
                        return Err(pyo3::exceptions::PyTypeError::new_err(concat!(
                            $key,
                            " must not be None"
                        )));
                    }
                    #[allow(clippy::redundant_closure_call)]
                    ($body)(py_val.extract()?);
                    set_fields |= $flag;
                }
            };
        }

        /// Extract an optional (None-able) value for a field.
        macro_rules! set_opt_field {
            ($key:literal, $flag:expr, $body:expr) => {
                if let Some(py_val) = kwargs.get_item($key)? {
                    #[allow(clippy::redundant_closure_call)]
                    if py_val.is_none() {
                        ($body)(None);
                    } else {
                        ($body)(Some(py_val.extract()?));
                    }
                    set_fields |= $flag;
                }
            };
        }

        set_field!("display", F_DISPLAY, |v: Display| {
            style.display = (&v).into()
        });
        set_field!("box_sizing", F_BOX_SIZING, |v: BoxSizing| {
            style.box_sizing = (&v).into()
        });
        set_field!("overflow_x", F_OVERFLOW_X, |v: Overflow| {
            style.overflow.x = (&v).into()
        });
        set_field!("overflow_y", F_OVERFLOW_Y, |v: Overflow| {
            style.overflow.y = (&v).into()
        });
        set_field!("scrollbar_width", F_SCROLLBAR_WIDTH, |v: f32| {
            style.scrollbar_width = v
        });
        set_field!("position", F_POSITION, |v: Position| {
            style.position = (&v).into()
        });

        // Inset
        set_field!("inset_left", F_INSET_LEFT, |v: LengthPercentageAuto| {
            style.inset.left = (&v).into()
        });
        set_field!("inset_right", F_INSET_RIGHT, |v: LengthPercentageAuto| {
            style.inset.right = (&v).into()
        });
        set_field!("inset_top", F_INSET_TOP, |v: LengthPercentageAuto| {
            style.inset.top = (&v).into()
        });
        set_field!(
            "inset_bottom",
            F_INSET_BOTTOM,
            |v: LengthPercentageAuto| { style.inset.bottom = (&v).into() }
        );

        // Size
        set_field!("size_width", F_SIZE_WIDTH, |v: Dimension| {
            style.size.width = (&v).into()
        });
        set_field!("size_height", F_SIZE_HEIGHT, |v: Dimension| {
            style.size.height = (&v).into()
        });
        set_field!("min_size_width", F_MIN_SIZE_WIDTH, |v: Dimension| {
            style.min_size.width = (&v).into()
        });
        set_field!("min_size_height", F_MIN_SIZE_HEIGHT, |v: Dimension| {
            style.min_size.height = (&v).into()
        });
        set_field!("max_size_width", F_MAX_SIZE_WIDTH, |v: Dimension| {
            style.max_size.width = (&v).into()
        });
        set_field!("max_size_height", F_MAX_SIZE_HEIGHT, |v: Dimension| {
            style.max_size.height = (&v).into()
        });
        set_opt_field!("aspect_ratio", F_ASPECT_RATIO, |v: Option<f32>| {
            style.aspect_ratio = v
        });

        // Margin
        set_field!("margin_left", F_MARGIN_LEFT, |v: LengthPercentageAuto| {
            style.margin.left = (&v).into()
        });
        set_field!(
            "margin_right",
            F_MARGIN_RIGHT,
            |v: LengthPercentageAuto| { style.margin.right = (&v).into() }
        );
        set_field!("margin_top", F_MARGIN_TOP, |v: LengthPercentageAuto| {
            style.margin.top = (&v).into()
        });
        set_field!(
            "margin_bottom",
            F_MARGIN_BOTTOM,
            |v: LengthPercentageAuto| { style.margin.bottom = (&v).into() }
        );

        // Padding
        set_field!("padding_left", F_PADDING_LEFT, |v: LengthPercentage| {
            style.padding.left = (&v).into()
        });
        set_field!("padding_right", F_PADDING_RIGHT, |v: LengthPercentage| {
            style.padding.right = (&v).into()
        });
        set_field!("padding_top", F_PADDING_TOP, |v: LengthPercentage| {
            style.padding.top = (&v).into()
        });
        set_field!(
            "padding_bottom",
            F_PADDING_BOTTOM,
            |v: LengthPercentage| { style.padding.bottom = (&v).into() }
        );

        // Border
        set_field!("border_left", F_BORDER_LEFT, |v: LengthPercentage| {
            style.border.left = (&v).into()
        });
        set_field!("border_right", F_BORDER_RIGHT, |v: LengthPercentage| {
            style.border.right = (&v).into()
        });
        set_field!("border_top", F_BORDER_TOP, |v: LengthPercentage| {
            style.border.top = (&v).into()
        });
        set_field!("border_bottom", F_BORDER_BOTTOM, |v: LengthPercentage| {
            style.border.bottom = (&v).into()
        });

        // Alignment (these accept None to explicitly clear)
        set_opt_field!("align_items", F_ALIGN_ITEMS, |v: Option<AlignItems>| {
            style.align_items = opt_align_items_to_taffy(&v)
        });
        set_opt_field!("align_self", F_ALIGN_SELF, |v: Option<AlignItems>| {
            style.align_self = opt_align_items_to_taffy(&v)
        });
        set_opt_field!(
            "justify_items",
            F_JUSTIFY_ITEMS,
            |v: Option<AlignItems>| { style.justify_items = opt_align_items_to_taffy(&v) }
        );
        set_opt_field!(
            "justify_self",
            F_JUSTIFY_SELF,
            |v: Option<AlignItems>| { style.justify_self = opt_align_items_to_taffy(&v) }
        );
        set_opt_field!(
            "align_content",
            F_ALIGN_CONTENT,
            |v: Option<AlignContent>| { style.align_content = opt_align_content_to_taffy(&v) }
        );
        set_opt_field!(
            "justify_content",
            F_JUSTIFY_CONTENT,
            |v: Option<AlignContent>| { style.justify_content = opt_align_content_to_taffy(&v) }
        );

        // Gap
        set_field!("gap_width", F_GAP_WIDTH, |v: LengthPercentage| {
            style.gap.width = (&v).into()
        });
        set_field!("gap_height", F_GAP_HEIGHT, |v: LengthPercentage| {
            style.gap.height = (&v).into()
        });

        // Block
        set_field!("text_align", F_TEXT_ALIGN, |v: TextAlign| {
            style.text_align = (&v).into()
        });

        // Flexbox
        set_field!("flex_direction", F_FLEX_DIRECTION, |v: FlexDirection| {
            style.flex_direction = (&v).into()
        });
        set_field!("flex_wrap", F_FLEX_WRAP, |v: FlexWrap| {
            style.flex_wrap = (&v).into()
        });
        set_field!("flex_basis", F_FLEX_BASIS, |v: Dimension| {
            style.flex_basis = (&v).into()
        });
        set_field!("flex_grow", F_FLEX_GROW, |v: f32| style.flex_grow = v);
        set_field!("flex_shrink", F_FLEX_SHRINK, |v: f32| {
            style.flex_shrink = v
        });

        // Grid
        set_field!(
            "grid_template_rows",
            F_GRID_TEMPLATE_ROWS,
            |v: Vec<GridTrack>| { style.grid_template_rows = tracks_to_taffy(&v) }
        );
        set_field!(
            "grid_template_columns",
            F_GRID_TEMPLATE_COLUMNS,
            |v: Vec<GridTrack>| { style.grid_template_columns = tracks_to_taffy(&v) }
        );
        set_field!(
            "grid_auto_rows",
            F_GRID_AUTO_ROWS,
            |v: Vec<GridTrack>| { style.grid_auto_rows = auto_tracks_to_taffy(&v) }
        );
        set_field!(
            "grid_auto_columns",
            F_GRID_AUTO_COLUMNS,
            |v: Vec<GridTrack>| { style.grid_auto_columns = auto_tracks_to_taffy(&v) }
        );
        set_field!("grid_auto_flow", F_GRID_AUTO_FLOW, |v: GridAutoFlow| {
            style.grid_auto_flow = (&v).into()
        });
        set_field!("grid_row", F_GRID_ROW, |v: GridLine| {
            style.grid_row = (&v).into()
        });
        set_field!("grid_column", F_GRID_COLUMN, |v: GridLine| {
            style.grid_column = (&v).into()
        });

        Ok(Self {
            inner: style,
            set_fields,
        })
    }

    // --- Getters and Setters ---

    #[getter]
    fn get_display(&self) -> Display {
        self.inner.display.into()
    }
    #[setter]
    fn set_display(&mut self, value: Display) {
        self.inner.display = (&value).into();
        self.set_fields |= F_DISPLAY;
    }

    #[getter]
    fn get_box_sizing(&self) -> BoxSizing {
        self.inner.box_sizing.into()
    }
    #[setter]
    fn set_box_sizing(&mut self, value: BoxSizing) {
        self.inner.box_sizing = (&value).into();
        self.set_fields |= F_BOX_SIZING;
    }

    #[getter]
    fn get_overflow_x(&self) -> Overflow {
        self.inner.overflow.x.into()
    }
    #[setter]
    fn set_overflow_x(&mut self, value: Overflow) {
        self.inner.overflow.x = (&value).into();
        self.set_fields |= F_OVERFLOW_X;
    }

    #[getter]
    fn get_overflow_y(&self) -> Overflow {
        self.inner.overflow.y.into()
    }
    #[setter]
    fn set_overflow_y(&mut self, value: Overflow) {
        self.inner.overflow.y = (&value).into();
        self.set_fields |= F_OVERFLOW_Y;
    }

    #[getter]
    fn get_scrollbar_width(&self) -> f32 {
        self.inner.scrollbar_width
    }
    #[setter]
    fn set_scrollbar_width(&mut self, value: f32) {
        self.inner.scrollbar_width = value;
        self.set_fields |= F_SCROLLBAR_WIDTH;
    }

    #[getter]
    fn get_position(&self) -> Position {
        self.inner.position.into()
    }
    #[setter]
    fn set_position(&mut self, value: Position) {
        self.inner.position = (&value).into();
        self.set_fields |= F_POSITION;
    }

    // Inset
    #[getter]
    fn get_inset_left(&self) -> LengthPercentageAuto {
        self.inner.inset.left.into()
    }
    #[setter]
    fn set_inset_left(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.left = (&value).into();
        self.set_fields |= F_INSET_LEFT;
    }
    #[getter]
    fn get_inset_right(&self) -> LengthPercentageAuto {
        self.inner.inset.right.into()
    }
    #[setter]
    fn set_inset_right(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.right = (&value).into();
        self.set_fields |= F_INSET_RIGHT;
    }
    #[getter]
    fn get_inset_top(&self) -> LengthPercentageAuto {
        self.inner.inset.top.into()
    }
    #[setter]
    fn set_inset_top(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.top = (&value).into();
        self.set_fields |= F_INSET_TOP;
    }
    #[getter]
    fn get_inset_bottom(&self) -> LengthPercentageAuto {
        self.inner.inset.bottom.into()
    }
    #[setter]
    fn set_inset_bottom(&mut self, value: LengthPercentageAuto) {
        self.inner.inset.bottom = (&value).into();
        self.set_fields |= F_INSET_BOTTOM;
    }

    // Size
    #[getter]
    fn get_size_width(&self) -> Dimension {
        self.inner.size.width.into()
    }
    #[setter]
    fn set_size_width(&mut self, value: Dimension) {
        self.inner.size.width = (&value).into();
        self.set_fields |= F_SIZE_WIDTH;
    }
    #[getter]
    fn get_size_height(&self) -> Dimension {
        self.inner.size.height.into()
    }
    #[setter]
    fn set_size_height(&mut self, value: Dimension) {
        self.inner.size.height = (&value).into();
        self.set_fields |= F_SIZE_HEIGHT;
    }
    #[getter]
    fn get_min_size_width(&self) -> Dimension {
        self.inner.min_size.width.into()
    }
    #[setter]
    fn set_min_size_width(&mut self, value: Dimension) {
        self.inner.min_size.width = (&value).into();
        self.set_fields |= F_MIN_SIZE_WIDTH;
    }
    #[getter]
    fn get_min_size_height(&self) -> Dimension {
        self.inner.min_size.height.into()
    }
    #[setter]
    fn set_min_size_height(&mut self, value: Dimension) {
        self.inner.min_size.height = (&value).into();
        self.set_fields |= F_MIN_SIZE_HEIGHT;
    }
    #[getter]
    fn get_max_size_width(&self) -> Dimension {
        self.inner.max_size.width.into()
    }
    #[setter]
    fn set_max_size_width(&mut self, value: Dimension) {
        self.inner.max_size.width = (&value).into();
        self.set_fields |= F_MAX_SIZE_WIDTH;
    }
    #[getter]
    fn get_max_size_height(&self) -> Dimension {
        self.inner.max_size.height.into()
    }
    #[setter]
    fn set_max_size_height(&mut self, value: Dimension) {
        self.inner.max_size.height = (&value).into();
        self.set_fields |= F_MAX_SIZE_HEIGHT;
    }

    #[getter]
    fn get_aspect_ratio(&self) -> Option<f32> {
        self.inner.aspect_ratio
    }
    #[setter]
    fn set_aspect_ratio(&mut self, value: Option<f32>) {
        self.inner.aspect_ratio = value;
        self.set_fields |= F_ASPECT_RATIO;
    }

    // Margin
    #[getter]
    fn get_margin_left(&self) -> LengthPercentageAuto {
        self.inner.margin.left.into()
    }
    #[setter]
    fn set_margin_left(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.left = (&value).into();
        self.set_fields |= F_MARGIN_LEFT;
    }
    #[getter]
    fn get_margin_right(&self) -> LengthPercentageAuto {
        self.inner.margin.right.into()
    }
    #[setter]
    fn set_margin_right(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.right = (&value).into();
        self.set_fields |= F_MARGIN_RIGHT;
    }
    #[getter]
    fn get_margin_top(&self) -> LengthPercentageAuto {
        self.inner.margin.top.into()
    }
    #[setter]
    fn set_margin_top(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.top = (&value).into();
        self.set_fields |= F_MARGIN_TOP;
    }
    #[getter]
    fn get_margin_bottom(&self) -> LengthPercentageAuto {
        self.inner.margin.bottom.into()
    }
    #[setter]
    fn set_margin_bottom(&mut self, value: LengthPercentageAuto) {
        self.inner.margin.bottom = (&value).into();
        self.set_fields |= F_MARGIN_BOTTOM;
    }

    // Padding
    #[getter]
    fn get_padding_left(&self) -> LengthPercentage {
        self.inner.padding.left.into()
    }
    #[setter]
    fn set_padding_left(&mut self, value: LengthPercentage) {
        self.inner.padding.left = (&value).into();
        self.set_fields |= F_PADDING_LEFT;
    }
    #[getter]
    fn get_padding_right(&self) -> LengthPercentage {
        self.inner.padding.right.into()
    }
    #[setter]
    fn set_padding_right(&mut self, value: LengthPercentage) {
        self.inner.padding.right = (&value).into();
        self.set_fields |= F_PADDING_RIGHT;
    }
    #[getter]
    fn get_padding_top(&self) -> LengthPercentage {
        self.inner.padding.top.into()
    }
    #[setter]
    fn set_padding_top(&mut self, value: LengthPercentage) {
        self.inner.padding.top = (&value).into();
        self.set_fields |= F_PADDING_TOP;
    }
    #[getter]
    fn get_padding_bottom(&self) -> LengthPercentage {
        self.inner.padding.bottom.into()
    }
    #[setter]
    fn set_padding_bottom(&mut self, value: LengthPercentage) {
        self.inner.padding.bottom = (&value).into();
        self.set_fields |= F_PADDING_BOTTOM;
    }

    // Border
    #[getter]
    fn get_border_left(&self) -> LengthPercentage {
        self.inner.border.left.into()
    }
    #[setter]
    fn set_border_left(&mut self, value: LengthPercentage) {
        self.inner.border.left = (&value).into();
        self.set_fields |= F_BORDER_LEFT;
    }
    #[getter]
    fn get_border_right(&self) -> LengthPercentage {
        self.inner.border.right.into()
    }
    #[setter]
    fn set_border_right(&mut self, value: LengthPercentage) {
        self.inner.border.right = (&value).into();
        self.set_fields |= F_BORDER_RIGHT;
    }
    #[getter]
    fn get_border_top(&self) -> LengthPercentage {
        self.inner.border.top.into()
    }
    #[setter]
    fn set_border_top(&mut self, value: LengthPercentage) {
        self.inner.border.top = (&value).into();
        self.set_fields |= F_BORDER_TOP;
    }
    #[getter]
    fn get_border_bottom(&self) -> LengthPercentage {
        self.inner.border.bottom.into()
    }
    #[setter]
    fn set_border_bottom(&mut self, value: LengthPercentage) {
        self.inner.border.bottom = (&value).into();
        self.set_fields |= F_BORDER_BOTTOM;
    }

    // Alignment
    #[getter]
    fn get_align_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_items)
    }
    #[setter]
    fn set_align_items(&mut self, value: Option<AlignItems>) {
        self.inner.align_items = opt_align_items_to_taffy(&value);
        self.set_fields |= F_ALIGN_ITEMS;
    }

    #[getter]
    fn get_align_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_self)
    }
    #[setter]
    fn set_align_self(&mut self, value: Option<AlignItems>) {
        self.inner.align_self = opt_align_items_to_taffy(&value);
        self.set_fields |= F_ALIGN_SELF;
    }

    #[getter]
    fn get_justify_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_items)
    }
    #[setter]
    fn set_justify_items(&mut self, value: Option<AlignItems>) {
        self.inner.justify_items = opt_align_items_to_taffy(&value);
        self.set_fields |= F_JUSTIFY_ITEMS;
    }

    #[getter]
    fn get_justify_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_self)
    }
    #[setter]
    fn set_justify_self(&mut self, value: Option<AlignItems>) {
        self.inner.justify_self = opt_align_items_to_taffy(&value);
        self.set_fields |= F_JUSTIFY_SELF;
    }

    #[getter]
    fn get_align_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.align_content)
    }
    #[setter]
    fn set_align_content(&mut self, value: Option<AlignContent>) {
        self.inner.align_content = opt_align_content_to_taffy(&value);
        self.set_fields |= F_ALIGN_CONTENT;
    }

    #[getter]
    fn get_justify_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.justify_content)
    }
    #[setter]
    fn set_justify_content(&mut self, value: Option<AlignContent>) {
        self.inner.justify_content = opt_align_content_to_taffy(&value);
        self.set_fields |= F_JUSTIFY_CONTENT;
    }

    // Gap
    #[getter]
    fn get_gap_width(&self) -> LengthPercentage {
        self.inner.gap.width.into()
    }
    #[setter]
    fn set_gap_width(&mut self, value: LengthPercentage) {
        self.inner.gap.width = (&value).into();
        self.set_fields |= F_GAP_WIDTH;
    }
    #[getter]
    fn get_gap_height(&self) -> LengthPercentage {
        self.inner.gap.height.into()
    }
    #[setter]
    fn set_gap_height(&mut self, value: LengthPercentage) {
        self.inner.gap.height = (&value).into();
        self.set_fields |= F_GAP_HEIGHT;
    }

    // Block
    #[getter]
    fn get_text_align(&self) -> TextAlign {
        self.inner.text_align.into()
    }
    #[setter]
    fn set_text_align(&mut self, value: TextAlign) {
        self.inner.text_align = (&value).into();
        self.set_fields |= F_TEXT_ALIGN;
    }

    // Flexbox
    #[getter]
    fn get_flex_direction(&self) -> FlexDirection {
        self.inner.flex_direction.into()
    }
    #[setter]
    fn set_flex_direction(&mut self, value: FlexDirection) {
        self.inner.flex_direction = (&value).into();
        self.set_fields |= F_FLEX_DIRECTION;
    }

    #[getter]
    fn get_flex_wrap(&self) -> FlexWrap {
        self.inner.flex_wrap.into()
    }
    #[setter]
    fn set_flex_wrap(&mut self, value: FlexWrap) {
        self.inner.flex_wrap = (&value).into();
        self.set_fields |= F_FLEX_WRAP;
    }

    #[getter]
    fn get_flex_basis(&self) -> Dimension {
        self.inner.flex_basis.into()
    }
    #[setter]
    fn set_flex_basis(&mut self, value: Dimension) {
        self.inner.flex_basis = (&value).into();
        self.set_fields |= F_FLEX_BASIS;
    }

    #[getter]
    fn get_flex_grow(&self) -> f32 {
        self.inner.flex_grow
    }
    #[setter]
    fn set_flex_grow(&mut self, value: f32) {
        self.inner.flex_grow = value;
        self.set_fields |= F_FLEX_GROW;
    }

    #[getter]
    fn get_flex_shrink(&self) -> f32 {
        self.inner.flex_shrink
    }
    #[setter]
    fn set_flex_shrink(&mut self, value: f32) {
        self.inner.flex_shrink = value;
        self.set_fields |= F_FLEX_SHRINK;
    }

    // Grid
    #[getter]
    fn get_grid_template_rows(&self) -> Vec<GridTrack> {
        tracks_from_taffy(&self.inner.grid_template_rows)
    }
    #[setter]
    fn set_grid_template_rows(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_template_rows = tracks_to_taffy(&value);
        self.set_fields |= F_GRID_TEMPLATE_ROWS;
    }

    #[getter]
    fn get_grid_template_columns(&self) -> Vec<GridTrack> {
        tracks_from_taffy(&self.inner.grid_template_columns)
    }
    #[setter]
    fn set_grid_template_columns(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_template_columns = tracks_to_taffy(&value);
        self.set_fields |= F_GRID_TEMPLATE_COLUMNS;
    }

    #[getter]
    fn get_grid_auto_rows(&self) -> Vec<GridTrack> {
        auto_tracks_from_taffy(&self.inner.grid_auto_rows)
    }
    #[setter]
    fn set_grid_auto_rows(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_auto_rows = auto_tracks_to_taffy(&value);
        self.set_fields |= F_GRID_AUTO_ROWS;
    }

    #[getter]
    fn get_grid_auto_columns(&self) -> Vec<GridTrack> {
        auto_tracks_from_taffy(&self.inner.grid_auto_columns)
    }
    #[setter]
    fn set_grid_auto_columns(&mut self, value: Vec<GridTrack>) {
        self.inner.grid_auto_columns = auto_tracks_to_taffy(&value);
        self.set_fields |= F_GRID_AUTO_COLUMNS;
    }

    #[getter]
    fn get_grid_auto_flow(&self) -> GridAutoFlow {
        self.inner.grid_auto_flow.into()
    }
    #[setter]
    fn set_grid_auto_flow(&mut self, value: GridAutoFlow) {
        self.inner.grid_auto_flow = (&value).into();
        self.set_fields |= F_GRID_AUTO_FLOW;
    }

    #[getter]
    fn get_grid_row(&self) -> GridLine {
        self.inner.grid_row.clone().into()
    }
    #[setter]
    fn set_grid_row(&mut self, value: GridLine) {
        self.inner.grid_row = (&value).into();
        self.set_fields |= F_GRID_ROW;
    }

    #[getter]
    fn get_grid_column(&self) -> GridLine {
        self.inner.grid_column.clone().into()
    }
    #[setter]
    fn set_grid_column(&mut self, value: GridLine) {
        self.inner.grid_column = (&value).into();
        self.set_fields |= F_GRID_COLUMN;
    }

    fn __repr__(&self) -> String {
        format!(
            "Style(display={:?}, position={:?})",
            self.inner.display, self.inner.position
        )
    }

    /// Merge two styles: `self | other`. Fields explicitly set in `other` override
    /// those in `self`. Fields not set in `other` are preserved from `self`.
    fn __or__(&self, other: &Style) -> Style {
        let mut result = self.clone();
        let rhs = other.set_fields;

        if rhs & F_DISPLAY != 0 {
            result.inner.display = other.inner.display;
        }
        if rhs & F_BOX_SIZING != 0 {
            result.inner.box_sizing = other.inner.box_sizing;
        }
        if rhs & F_OVERFLOW_X != 0 {
            result.inner.overflow.x = other.inner.overflow.x;
        }
        if rhs & F_OVERFLOW_Y != 0 {
            result.inner.overflow.y = other.inner.overflow.y;
        }
        if rhs & F_SCROLLBAR_WIDTH != 0 {
            result.inner.scrollbar_width = other.inner.scrollbar_width;
        }
        if rhs & F_POSITION != 0 {
            result.inner.position = other.inner.position;
        }
        if rhs & F_INSET_LEFT != 0 {
            result.inner.inset.left = other.inner.inset.left;
        }
        if rhs & F_INSET_RIGHT != 0 {
            result.inner.inset.right = other.inner.inset.right;
        }
        if rhs & F_INSET_TOP != 0 {
            result.inner.inset.top = other.inner.inset.top;
        }
        if rhs & F_INSET_BOTTOM != 0 {
            result.inner.inset.bottom = other.inner.inset.bottom;
        }
        if rhs & F_SIZE_WIDTH != 0 {
            result.inner.size.width = other.inner.size.width;
        }
        if rhs & F_SIZE_HEIGHT != 0 {
            result.inner.size.height = other.inner.size.height;
        }
        if rhs & F_MIN_SIZE_WIDTH != 0 {
            result.inner.min_size.width = other.inner.min_size.width;
        }
        if rhs & F_MIN_SIZE_HEIGHT != 0 {
            result.inner.min_size.height = other.inner.min_size.height;
        }
        if rhs & F_MAX_SIZE_WIDTH != 0 {
            result.inner.max_size.width = other.inner.max_size.width;
        }
        if rhs & F_MAX_SIZE_HEIGHT != 0 {
            result.inner.max_size.height = other.inner.max_size.height;
        }
        if rhs & F_ASPECT_RATIO != 0 {
            result.inner.aspect_ratio = other.inner.aspect_ratio;
        }
        if rhs & F_MARGIN_LEFT != 0 {
            result.inner.margin.left = other.inner.margin.left;
        }
        if rhs & F_MARGIN_RIGHT != 0 {
            result.inner.margin.right = other.inner.margin.right;
        }
        if rhs & F_MARGIN_TOP != 0 {
            result.inner.margin.top = other.inner.margin.top;
        }
        if rhs & F_MARGIN_BOTTOM != 0 {
            result.inner.margin.bottom = other.inner.margin.bottom;
        }
        if rhs & F_PADDING_LEFT != 0 {
            result.inner.padding.left = other.inner.padding.left;
        }
        if rhs & F_PADDING_RIGHT != 0 {
            result.inner.padding.right = other.inner.padding.right;
        }
        if rhs & F_PADDING_TOP != 0 {
            result.inner.padding.top = other.inner.padding.top;
        }
        if rhs & F_PADDING_BOTTOM != 0 {
            result.inner.padding.bottom = other.inner.padding.bottom;
        }
        if rhs & F_BORDER_LEFT != 0 {
            result.inner.border.left = other.inner.border.left;
        }
        if rhs & F_BORDER_RIGHT != 0 {
            result.inner.border.right = other.inner.border.right;
        }
        if rhs & F_BORDER_TOP != 0 {
            result.inner.border.top = other.inner.border.top;
        }
        if rhs & F_BORDER_BOTTOM != 0 {
            result.inner.border.bottom = other.inner.border.bottom;
        }
        if rhs & F_ALIGN_ITEMS != 0 {
            result.inner.align_items = other.inner.align_items;
        }
        if rhs & F_ALIGN_SELF != 0 {
            result.inner.align_self = other.inner.align_self;
        }
        if rhs & F_JUSTIFY_ITEMS != 0 {
            result.inner.justify_items = other.inner.justify_items;
        }
        if rhs & F_JUSTIFY_SELF != 0 {
            result.inner.justify_self = other.inner.justify_self;
        }
        if rhs & F_ALIGN_CONTENT != 0 {
            result.inner.align_content = other.inner.align_content;
        }
        if rhs & F_JUSTIFY_CONTENT != 0 {
            result.inner.justify_content = other.inner.justify_content;
        }
        if rhs & F_GAP_WIDTH != 0 {
            result.inner.gap.width = other.inner.gap.width;
        }
        if rhs & F_GAP_HEIGHT != 0 {
            result.inner.gap.height = other.inner.gap.height;
        }
        if rhs & F_TEXT_ALIGN != 0 {
            result.inner.text_align = other.inner.text_align;
        }
        if rhs & F_FLEX_DIRECTION != 0 {
            result.inner.flex_direction = other.inner.flex_direction;
        }
        if rhs & F_FLEX_WRAP != 0 {
            result.inner.flex_wrap = other.inner.flex_wrap;
        }
        if rhs & F_FLEX_BASIS != 0 {
            result.inner.flex_basis = other.inner.flex_basis;
        }
        if rhs & F_FLEX_GROW != 0 {
            result.inner.flex_grow = other.inner.flex_grow;
        }
        if rhs & F_FLEX_SHRINK != 0 {
            result.inner.flex_shrink = other.inner.flex_shrink;
        }
        if rhs & F_GRID_TEMPLATE_ROWS != 0 {
            result.inner.grid_template_rows = other.inner.grid_template_rows.clone();
        }
        if rhs & F_GRID_TEMPLATE_COLUMNS != 0 {
            result.inner.grid_template_columns = other.inner.grid_template_columns.clone();
        }
        if rhs & F_GRID_AUTO_ROWS != 0 {
            result.inner.grid_auto_rows = other.inner.grid_auto_rows.clone();
        }
        if rhs & F_GRID_AUTO_COLUMNS != 0 {
            result.inner.grid_auto_columns = other.inner.grid_auto_columns.clone();
        }
        if rhs & F_GRID_AUTO_FLOW != 0 {
            result.inner.grid_auto_flow = other.inner.grid_auto_flow;
        }
        if rhs & F_GRID_ROW != 0 {
            result.inner.grid_row = other.inner.grid_row.clone();
        }
        if rhs & F_GRID_COLUMN != 0 {
            result.inner.grid_column = other.inner.grid_column.clone();
        }

        // Merge the set_fields bitmask: result has everything self had plus everything other set.
        result.set_fields |= rhs;

        result
    }
}

impl From<&taffy::Style> for Style {
    fn from(s: &taffy::Style) -> Self {
        Self {
            inner: s.clone(),
            // When converting from a taffy::Style, we don't know which fields were
            // explicitly set, so we mark all fields as set.
            set_fields: u64::MAX,
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Style>()?;
    Ok(())
}
