use std::sync::OnceLock;

use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFrozenSet, PyString};

use crate::enums::{
    AlignContent, AlignItems, BoxSizing, Clear, Contain, Direction, Display, FlexDirection,
    FlexWrap, Float, GridAutoFlow, Overflow, Position, TextAlign,
};
use crate::errors::InvalidFlexLineCount;
use crate::geometry::hash_f32;
use crate::values::{
    dimension_to_py, grid_track_to_py, hash_taffy_compact_length, hash_taffy_grid_placement,
    hash_taffy_template_area, hash_taffy_template_component, hash_taffy_track_sizing_function,
    length_percentage_auto_to_py, length_percentage_to_py, DimensionInput, FlexBasisInput,
    GridPlacement, GridTemplateAreas, GridTemplateInput, GridTrackInput, LengthPercentageAutoInput,
    LengthPercentageInput, NoCalc, Repeat,
};

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
const F_DIRECTION: u64 = 1 << 50;
const F_CONTAIN: u64 = 1 << 51;
const F_FLOAT: u64 = 1 << 52;
const F_CLEAR: u64 = 1 << 53;
const F_FLEX_LINE_COUNT: u64 = 1 << 54;
const F_ITEM_IS_TABLE: u64 = 1 << 55;
const F_ITEM_IS_REPLACED: u64 = 1 << 56;
const F_GRID_TEMPLATE_ROW_NAMES: u64 = 1 << 57;
const F_GRID_TEMPLATE_COLUMN_NAMES: u64 = 1 << 58;
const F_GRID_TEMPLATE_AREAS: u64 = 1 << 59;

/// Every field's keyword name and flag, in declaration order.
///
/// `fields_set`, `__repr__` and `ALL_FIELDS` walk this table. Adding a field also means adding
/// its `F_*` constant, a `match` arm in `new`, a line in `copy_fields`, a getter, a line in
/// `compute_hash`, the stub, and an entry in `tests/test_style.py`'s non-default values, whose
/// tests check this table against the getters.
const FIELDS: &[(&str, u64)] = &[
    ("display", F_DISPLAY),
    ("box_sizing", F_BOX_SIZING),
    ("overflow_x", F_OVERFLOW_X),
    ("overflow_y", F_OVERFLOW_Y),
    ("scrollbar_width", F_SCROLLBAR_WIDTH),
    ("position", F_POSITION),
    ("direction", F_DIRECTION),
    ("contain", F_CONTAIN),
    ("float", F_FLOAT),
    ("clear", F_CLEAR),
    ("item_is_table", F_ITEM_IS_TABLE),
    ("item_is_replaced", F_ITEM_IS_REPLACED),
    ("inset_left", F_INSET_LEFT),
    ("inset_right", F_INSET_RIGHT),
    ("inset_top", F_INSET_TOP),
    ("inset_bottom", F_INSET_BOTTOM),
    ("size_width", F_SIZE_WIDTH),
    ("size_height", F_SIZE_HEIGHT),
    ("min_size_width", F_MIN_SIZE_WIDTH),
    ("min_size_height", F_MIN_SIZE_HEIGHT),
    ("max_size_width", F_MAX_SIZE_WIDTH),
    ("max_size_height", F_MAX_SIZE_HEIGHT),
    ("aspect_ratio", F_ASPECT_RATIO),
    ("margin_left", F_MARGIN_LEFT),
    ("margin_right", F_MARGIN_RIGHT),
    ("margin_top", F_MARGIN_TOP),
    ("margin_bottom", F_MARGIN_BOTTOM),
    ("padding_left", F_PADDING_LEFT),
    ("padding_right", F_PADDING_RIGHT),
    ("padding_top", F_PADDING_TOP),
    ("padding_bottom", F_PADDING_BOTTOM),
    ("border_left", F_BORDER_LEFT),
    ("border_right", F_BORDER_RIGHT),
    ("border_top", F_BORDER_TOP),
    ("border_bottom", F_BORDER_BOTTOM),
    ("align_items", F_ALIGN_ITEMS),
    ("align_self", F_ALIGN_SELF),
    ("justify_items", F_JUSTIFY_ITEMS),
    ("justify_self", F_JUSTIFY_SELF),
    ("align_content", F_ALIGN_CONTENT),
    ("justify_content", F_JUSTIFY_CONTENT),
    ("gap_width", F_GAP_WIDTH),
    ("gap_height", F_GAP_HEIGHT),
    ("text_align", F_TEXT_ALIGN),
    ("flex_direction", F_FLEX_DIRECTION),
    ("flex_wrap", F_FLEX_WRAP),
    ("flex_basis", F_FLEX_BASIS),
    ("flex_grow", F_FLEX_GROW),
    ("flex_shrink", F_FLEX_SHRINK),
    ("flex_line_count", F_FLEX_LINE_COUNT),
    ("grid_template_rows", F_GRID_TEMPLATE_ROWS),
    ("grid_template_columns", F_GRID_TEMPLATE_COLUMNS),
    ("grid_template_row_names", F_GRID_TEMPLATE_ROW_NAMES),
    ("grid_template_column_names", F_GRID_TEMPLATE_COLUMN_NAMES),
    ("grid_template_areas", F_GRID_TEMPLATE_AREAS),
    ("grid_auto_rows", F_GRID_AUTO_ROWS),
    ("grid_auto_columns", F_GRID_AUTO_COLUMNS),
    ("grid_auto_flow", F_GRID_AUTO_FLOW),
    ("grid_row", F_GRID_ROW),
    ("grid_column", F_GRID_COLUMN),
];

/// The flags of every field in `FIELDS`.
const ALL_FIELDS: u64 = {
    let mut mask = 0;
    let mut i = 0;
    while i < FIELDS.len() {
        mask |= FIELDS[i].1;
        i += 1;
    }
    mask
};

/// Style properties for a layout node.
#[pyclass(frozen, from_py_object, module = "waxy")]
#[derive(Clone, Debug)]
pub struct Style {
    pub(crate) inner: NoCalc<taffy::Style>,
    /// Bitmask tracking which fields have been explicitly set.
    set_fields: u64,
    /// `__hash__`'s result, computed on first use. Only correct because no `Style` is mutated
    /// after `from_parts` builds it.
    hash: OnceLock<u64>,
}

impl Style {
    /// Build a `Style`. Every constructor goes through here, so it's the one place that creates
    /// the hash cache and checks that unset fields hold their default values.
    ///
    /// Equality and hashing compare `inner` whole, which only matches merge behavior if a field
    /// that isn't set always holds its `taffy::Style::DEFAULT` value.
    pub(crate) fn from_parts(inner: taffy::Style, set_fields: u64) -> Self {
        debug_assert_eq!(
            set_fields & !ALL_FIELDS,
            0,
            "set_fields has bits for no field"
        );
        debug_assert!(
            {
                // Reset the set fields rather than comparing them, since a set field can hold a
                // value that isn't equal to itself (a NaN `flex_grow`).
                let mut unset_fields_only = inner.clone();
                copy_fields(&mut unset_fields_only, &taffy::Style::DEFAULT, set_fields);
                unset_fields_only == taffy::Style::DEFAULT
            },
            "an unset field holds a non-default value"
        );
        Self {
            inner: NoCalc(inner),
            set_fields,
            hash: OnceLock::new(),
        }
    }

    pub(crate) fn to_taffy(&self) -> taffy::Style {
        self.inner.0.clone()
    }

    /// A `Style` holding `inner` whose set fields are the ones that differ from
    /// `taffy::Style::DEFAULT`, for displaying a stored style, which has no set-field bitmask.
    ///
    /// Copies one field at a time onto the default with `copy_fields`, so it needs no per-field
    /// code.
    pub(crate) fn with_non_default_fields_set(inner: &taffy::Style) -> Style {
        let mut mask = 0;
        for &(_, flag) in FIELDS {
            let mut only_this_field = taffy::Style::DEFAULT;
            copy_fields(&mut only_this_field, inner, flag);
            if only_this_field != taffy::Style::DEFAULT {
                mask |= flag;
            }
        }
        Style::from_parts(inner.clone(), mask)
    }

    fn compute_hash(&self) -> u64 {
        use std::hash::{Hash, Hasher};
        use std::mem::discriminant;
        let mut h = std::collections::hash_map::DefaultHasher::new();

        // Destructured without `..`, so a field added in a taffy upgrade is a compile error
        // here rather than a field silently left out of the hash.
        let taffy::Style {
            dummy: _,
            display,
            item_is_table,
            item_is_replaced,
            box_sizing,
            direction,
            overflow,
            scrollbar_width,
            contain,
            float,
            clear,
            position,
            inset,
            size,
            min_size,
            max_size,
            aspect_ratio,
            margin,
            padding,
            border,
            align_items,
            align_self,
            justify_items,
            justify_self,
            align_content,
            justify_content,
            gap,
            text_align,
            flex_direction,
            flex_wrap,
            flex_line_count,
            flex_basis,
            flex_grow,
            flex_shrink,
            grid_template_rows,
            grid_template_columns,
            grid_auto_rows,
            grid_auto_columns,
            grid_auto_flow,
            grid_template_areas,
            grid_template_column_names,
            grid_template_row_names,
            grid_row,
            grid_column,
        } = &*self.inner;

        self.set_fields.hash(&mut h);

        // Enum fields — use discriminant since taffy enums don't derive Hash.
        discriminant(display).hash(&mut h);
        discriminant(box_sizing).hash(&mut h);
        discriminant(&overflow.x).hash(&mut h);
        discriminant(&overflow.y).hash(&mut h);
        discriminant(position).hash(&mut h);
        discriminant(text_align).hash(&mut h);
        discriminant(flex_direction).hash(&mut h);
        discriminant(flex_wrap).hash(&mut h);
        discriminant(grid_auto_flow).hash(&mut h);
        discriminant(direction).hash(&mut h);
        discriminant(float).hash(&mut h);
        discriminant(clear).hash(&mut h);
        // taffy's Contain is a bitset struct, so hash the enum it maps to.
        (Contain::from(*contain) as u8).hash(&mut h);

        // Option<alignment> fields — taffy's alignment types are (keyword, safety) structs.
        for alignment in [align_items, align_self, justify_items, justify_self] {
            alignment
                .map(|v| (discriminant(&v.keyword), discriminant(&v.safety)))
                .hash(&mut h);
        }
        for alignment in [align_content, justify_content] {
            alignment
                .map(|v| (discriminant(&v.keyword), discriminant(&v.safety)))
                .hash(&mut h);
        }

        // Plain bool and integer fields.
        item_is_table.hash(&mut h);
        item_is_replaced.hash(&mut h);
        flex_line_count.hash(&mut h);

        // Plain f32 fields — normalize -0.0 (consistent with f32's IEEE
        // float equality used by taffy's derived PartialEq for these fields).
        hash_f32(*scrollbar_width, &mut h);
        hash_f32(*flex_grow, &mut h);
        hash_f32(*flex_shrink, &mut h);
        match aspect_ratio {
            Some(v) => {
                1u8.hash(&mut h);
                hash_f32(*v, &mut h);
            }
            None => 0u8.hash(&mut h),
        }

        // CompactLength fields — bit-exact, matching CompactLength's PartialEq.
        // Each field type (Dimension, LengthPercentage, etc.) wraps CompactLength;
        // into_raw() extracts it.
        for side in [inset, margin] {
            hash_taffy_compact_length(side.left.into_raw(), &mut h);
            hash_taffy_compact_length(side.right.into_raw(), &mut h);
            hash_taffy_compact_length(side.top.into_raw(), &mut h);
            hash_taffy_compact_length(side.bottom.into_raw(), &mut h);
        }
        for side in [padding, border] {
            hash_taffy_compact_length(side.left.into_raw(), &mut h);
            hash_taffy_compact_length(side.right.into_raw(), &mut h);
            hash_taffy_compact_length(side.top.into_raw(), &mut h);
            hash_taffy_compact_length(side.bottom.into_raw(), &mut h);
        }
        hash_taffy_compact_length(size.width.into_raw(), &mut h);
        hash_taffy_compact_length(size.height.into_raw(), &mut h);
        for bound in [min_size, max_size] {
            hash_taffy_compact_length(bound.width.into_raw(), &mut h);
            hash_taffy_compact_length(bound.height.into_raw(), &mut h);
        }
        hash_taffy_compact_length(gap.width.into_raw(), &mut h);
        hash_taffy_compact_length(gap.height.into_raw(), &mut h);
        hash_taffy_compact_length(flex_basis.into_raw(), &mut h);

        // Grid track Vecs.
        for tracks in [grid_auto_rows, grid_auto_columns] {
            tracks.len().hash(&mut h);
            for tsf in tracks {
                hash_taffy_track_sizing_function(*tsf, &mut h);
            }
        }
        for tracks in [grid_template_rows, grid_template_columns] {
            tracks.len().hash(&mut h);
            for comp in tracks {
                hash_taffy_template_component(comp, &mut h);
            }
        }
        grid_template_row_names.hash(&mut h);
        grid_template_column_names.hash(&mut h);
        match grid_template_areas {
            Some(areas) => {
                1u8.hash(&mut h);
                areas.row_count.hash(&mut h);
                areas.column_count.hash(&mut h);
                areas.areas.len().hash(&mut h);
                for area in &areas.areas {
                    hash_taffy_template_area(area, &mut h);
                }
            }
            None => 0u8.hash(&mut h),
        }

        // Grid placement fields.
        hash_taffy_grid_placement(&grid_row.start, &mut h);
        hash_taffy_grid_placement(&grid_row.end, &mut h);
        hash_taffy_grid_placement(&grid_column.start, &mut h);
        hash_taffy_grid_placement(&grid_column.end, &mut h);

        h.finish()
    }
}

/// Copy the fields whose flags are in `mask` from `src` to `dst`.
fn copy_fields(dst: &mut taffy::Style, src: &taffy::Style, mask: u64) {
    macro_rules! copy {
        // Copy field: dst.$($path).+ = src.$($path).+
        ($flag:expr, $($path:ident).+) => {
            if mask & $flag != 0 {
                dst.$($path).+ = src.$($path).+;
            }
        };
        // Clone field (for non-Copy types like Vec)
        (clone $flag:expr, $($path:ident).+) => {
            if mask & $flag != 0 {
                dst.$($path).+ = src.$($path).+.clone();
            }
        };
    }

    copy!(F_DISPLAY, display);
    copy!(F_BOX_SIZING, box_sizing);
    copy!(F_OVERFLOW_X, overflow.x);
    copy!(F_OVERFLOW_Y, overflow.y);
    copy!(F_SCROLLBAR_WIDTH, scrollbar_width);
    copy!(F_POSITION, position);
    copy!(F_DIRECTION, direction);
    copy!(F_CONTAIN, contain);
    copy!(F_FLOAT, float);
    copy!(F_CLEAR, clear);
    copy!(F_ITEM_IS_TABLE, item_is_table);
    copy!(F_ITEM_IS_REPLACED, item_is_replaced);

    // Inset
    copy!(F_INSET_LEFT, inset.left);
    copy!(F_INSET_RIGHT, inset.right);
    copy!(F_INSET_TOP, inset.top);
    copy!(F_INSET_BOTTOM, inset.bottom);

    // Size
    copy!(F_SIZE_WIDTH, size.width);
    copy!(F_SIZE_HEIGHT, size.height);
    copy!(F_MIN_SIZE_WIDTH, min_size.width);
    copy!(F_MIN_SIZE_HEIGHT, min_size.height);
    copy!(F_MAX_SIZE_WIDTH, max_size.width);
    copy!(F_MAX_SIZE_HEIGHT, max_size.height);
    copy!(F_ASPECT_RATIO, aspect_ratio);

    // Margin
    copy!(F_MARGIN_LEFT, margin.left);
    copy!(F_MARGIN_RIGHT, margin.right);
    copy!(F_MARGIN_TOP, margin.top);
    copy!(F_MARGIN_BOTTOM, margin.bottom);

    // Padding
    copy!(F_PADDING_LEFT, padding.left);
    copy!(F_PADDING_RIGHT, padding.right);
    copy!(F_PADDING_TOP, padding.top);
    copy!(F_PADDING_BOTTOM, padding.bottom);

    // Border
    copy!(F_BORDER_LEFT, border.left);
    copy!(F_BORDER_RIGHT, border.right);
    copy!(F_BORDER_TOP, border.top);
    copy!(F_BORDER_BOTTOM, border.bottom);

    // Alignment
    copy!(F_ALIGN_ITEMS, align_items);
    copy!(F_ALIGN_SELF, align_self);
    copy!(F_JUSTIFY_ITEMS, justify_items);
    copy!(F_JUSTIFY_SELF, justify_self);
    copy!(F_ALIGN_CONTENT, align_content);
    copy!(F_JUSTIFY_CONTENT, justify_content);

    // Gap
    copy!(F_GAP_WIDTH, gap.width);
    copy!(F_GAP_HEIGHT, gap.height);

    // Block
    copy!(F_TEXT_ALIGN, text_align);

    // Flexbox
    copy!(F_FLEX_DIRECTION, flex_direction);
    copy!(F_FLEX_WRAP, flex_wrap);
    copy!(F_FLEX_BASIS, flex_basis);
    copy!(F_FLEX_GROW, flex_grow);
    copy!(F_FLEX_SHRINK, flex_shrink);
    copy!(F_FLEX_LINE_COUNT, flex_line_count);

    // Grid
    copy!(clone F_GRID_TEMPLATE_ROWS, grid_template_rows);
    copy!(clone F_GRID_TEMPLATE_COLUMNS, grid_template_columns);
    copy!(clone F_GRID_TEMPLATE_ROW_NAMES, grid_template_row_names);
    copy!(clone F_GRID_TEMPLATE_COLUMN_NAMES, grid_template_column_names);
    copy!(clone F_GRID_TEMPLATE_AREAS, grid_template_areas);
    copy!(clone F_GRID_AUTO_ROWS, grid_auto_rows);
    copy!(clone F_GRID_AUTO_COLUMNS, grid_auto_columns);
    copy!(F_GRID_AUTO_FLOW, grid_auto_flow);
    copy!(clone F_GRID_ROW, grid_row);
    copy!(clone F_GRID_COLUMN, grid_column);
}

/// Note which keyword's value failed to extract, as pyo3 does for its own arguments.
fn note_keyword(py: Python<'_>, name: &str, error: impl Into<PyErr>) -> PyErr {
    let error = error.into();
    let note = format!("while processing '{name}'");
    // Like pyo3, keep the original error if adding the note fails.
    let _ = error.value(py).call_method1("add_note", (note,));
    error
}

fn opt_align_items_from_taffy(v: Option<taffy::AlignItems>) -> Option<AlignItems> {
    v.map(|a| a.into())
}

fn opt_align_items_to_taffy(v: &Option<AlignItems>) -> Option<taffy::AlignItems> {
    v.as_ref().map(|a| a.into())
}

fn opt_align_content_from_taffy(v: Option<taffy::AlignContent>) -> Option<AlignContent> {
    v.map(|a| a.into())
}

fn opt_align_content_to_taffy(v: &Option<AlignContent>) -> Option<taffy::AlignContent> {
    v.as_ref().map(|a| a.into())
}

fn tracks_to_taffy(
    py: Python<'_>,
    tracks: &[GridTemplateInput],
) -> Vec<taffy::style::GridTemplateComponent<String>> {
    tracks.iter().map(|t| t.to_taffy(py)).collect()
}

fn tracks_from_taffy(
    py: Python<'_>,
    tracks: &[taffy::style::GridTemplateComponent<String>],
) -> PyResult<Vec<Py<PyAny>>> {
    tracks
        .iter()
        .map(|t| match t {
            taffy::style::GridTemplateComponent::Single(tsf) => grid_track_to_py(py, *tsf),
            taffy::style::GridTemplateComponent::Repeat(r) => {
                Ok(Py::new(py, Repeat::from_taffy(py, r)?)?.into_any())
            }
        })
        .collect()
}

fn auto_tracks_to_taffy(
    py: Python<'_>,
    tracks: &[GridTrackInput],
) -> Vec<taffy::style::TrackSizingFunction> {
    tracks.iter().map(|t| t.to_taffy(py)).collect()
}

fn auto_tracks_from_taffy(
    py: Python<'_>,
    tracks: &[taffy::style::TrackSizingFunction],
) -> PyResult<Vec<Py<PyAny>>> {
    tracks.iter().map(|t| grid_track_to_py(py, *t)).collect()
}

#[pymethods]
impl Style {
    #[new]
    #[pyo3(signature = (**kwargs))]
    fn new(py: Python<'_>, kwargs: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut style = taffy::Style::DEFAULT;
        let mut set_fields: u64 = 0;

        let Some(kwargs) = kwargs else {
            return Ok(Self::from_parts(style, set_fields));
        };

        // Dispatch over the keywords actually passed, so an unknown keyword reaches the final
        // arm instead of being silently ignored.
        for (key, value) in kwargs.iter() {
            let key = key.cast_into::<PyString>()?;
            let name = key.to_str()?;

            /// Set a field from `value`. `None` means "use the default" (leave it unset).
            macro_rules! field {
                ($flag:expr, |$v:ident: $t:ty| $body:expr) => {
                    if !value.is_none() {
                        let $v: $t = value.extract().map_err(|e| note_keyword(py, name, e))?;
                        $body;
                        set_fields |= $flag;
                    }
                };
            }

            /// Set an optional field from `value`, where `None` explicitly clears it.
            macro_rules! opt_field {
                ($flag:expr, |$v:ident: $t:ty| $body:expr) => {{
                    let $v: Option<$t> = value.extract().map_err(|e| note_keyword(py, name, e))?;
                    $body;
                    set_fields |= $flag;
                }};
            }

            match name {
                "display" => field!(F_DISPLAY, |v: Display| style.display = (&v).into()),
                "box_sizing" => field!(F_BOX_SIZING, |v: BoxSizing| {
                    style.box_sizing = (&v).into()
                }),
                "overflow_x" => field!(F_OVERFLOW_X, |v: Overflow| {
                    style.overflow.x = (&v).into()
                }),
                "overflow_y" => field!(F_OVERFLOW_Y, |v: Overflow| {
                    style.overflow.y = (&v).into()
                }),
                "scrollbar_width" => {
                    field!(F_SCROLLBAR_WIDTH, |v: f32| { style.scrollbar_width = v })
                }
                "position" => field!(F_POSITION, |v: Position| style.position = (&v).into()),
                "direction" => field!(F_DIRECTION, |v: Direction| {
                    style.direction = (&v).into()
                }),
                "contain" => field!(F_CONTAIN, |v: Contain| style.contain = (&v).into()),
                "float" => field!(F_FLOAT, |v: Float| style.float = (&v).into()),
                "clear" => field!(F_CLEAR, |v: Clear| style.clear = (&v).into()),
                "item_is_table" => field!(F_ITEM_IS_TABLE, |v: bool| style.item_is_table = v),
                "item_is_replaced" => {
                    field!(F_ITEM_IS_REPLACED, |v: bool| { style.item_is_replaced = v })
                }

                // Inset
                "inset_left" => field!(F_INSET_LEFT, |v: LengthPercentageAutoInput| {
                    style.inset.left = v.to_taffy()
                }),
                "inset_right" => field!(F_INSET_RIGHT, |v: LengthPercentageAutoInput| {
                    style.inset.right = v.to_taffy()
                }),
                "inset_top" => field!(F_INSET_TOP, |v: LengthPercentageAutoInput| {
                    style.inset.top = v.to_taffy()
                }),
                "inset_bottom" => field!(F_INSET_BOTTOM, |v: LengthPercentageAutoInput| {
                    style.inset.bottom = v.to_taffy()
                }),

                // Size
                "size_width" => field!(F_SIZE_WIDTH, |v: DimensionInput| {
                    style.size.width = v.to_taffy(py)
                }),
                "size_height" => field!(F_SIZE_HEIGHT, |v: DimensionInput| {
                    style.size.height = v.to_taffy(py)
                }),
                "min_size_width" => field!(F_MIN_SIZE_WIDTH, |v: LengthPercentageAutoInput| {
                    style.min_size.width = v.to_taffy()
                }),
                "min_size_height" => field!(F_MIN_SIZE_HEIGHT, |v: LengthPercentageAutoInput| {
                    style.min_size.height = v.to_taffy()
                }),
                "max_size_width" => field!(F_MAX_SIZE_WIDTH, |v: LengthPercentageAutoInput| {
                    style.max_size.width = v.to_taffy()
                }),
                "max_size_height" => field!(F_MAX_SIZE_HEIGHT, |v: LengthPercentageAutoInput| {
                    style.max_size.height = v.to_taffy()
                }),
                "aspect_ratio" => opt_field!(F_ASPECT_RATIO, |v: f32| style.aspect_ratio = v),

                // Margin
                "margin_left" => field!(F_MARGIN_LEFT, |v: LengthPercentageAutoInput| {
                    style.margin.left = v.to_taffy()
                }),
                "margin_right" => field!(F_MARGIN_RIGHT, |v: LengthPercentageAutoInput| {
                    style.margin.right = v.to_taffy()
                }),
                "margin_top" => field!(F_MARGIN_TOP, |v: LengthPercentageAutoInput| {
                    style.margin.top = v.to_taffy()
                }),
                "margin_bottom" => field!(F_MARGIN_BOTTOM, |v: LengthPercentageAutoInput| {
                    style.margin.bottom = v.to_taffy()
                }),

                // Padding
                "padding_left" => field!(F_PADDING_LEFT, |v: LengthPercentageInput| {
                    style.padding.left = v.to_taffy()
                }),
                "padding_right" => field!(F_PADDING_RIGHT, |v: LengthPercentageInput| {
                    style.padding.right = v.to_taffy()
                }),
                "padding_top" => field!(F_PADDING_TOP, |v: LengthPercentageInput| {
                    style.padding.top = v.to_taffy()
                }),
                "padding_bottom" => field!(F_PADDING_BOTTOM, |v: LengthPercentageInput| {
                    style.padding.bottom = v.to_taffy()
                }),

                // Border
                "border_left" => field!(F_BORDER_LEFT, |v: LengthPercentageInput| {
                    style.border.left = v.to_taffy()
                }),
                "border_right" => field!(F_BORDER_RIGHT, |v: LengthPercentageInput| {
                    style.border.right = v.to_taffy()
                }),
                "border_top" => field!(F_BORDER_TOP, |v: LengthPercentageInput| {
                    style.border.top = v.to_taffy()
                }),
                "border_bottom" => field!(F_BORDER_BOTTOM, |v: LengthPercentageInput| {
                    style.border.bottom = v.to_taffy()
                }),

                // Alignment (these accept None to explicitly clear)
                "align_items" => opt_field!(F_ALIGN_ITEMS, |v: AlignItems| {
                    style.align_items = opt_align_items_to_taffy(&v)
                }),
                "align_self" => opt_field!(F_ALIGN_SELF, |v: AlignItems| {
                    style.align_self = opt_align_items_to_taffy(&v)
                }),
                "justify_items" => opt_field!(F_JUSTIFY_ITEMS, |v: AlignItems| {
                    style.justify_items = opt_align_items_to_taffy(&v)
                }),
                "justify_self" => opt_field!(F_JUSTIFY_SELF, |v: AlignItems| {
                    style.justify_self = opt_align_items_to_taffy(&v)
                }),
                "align_content" => opt_field!(F_ALIGN_CONTENT, |v: AlignContent| {
                    style.align_content = opt_align_content_to_taffy(&v)
                }),
                "justify_content" => opt_field!(F_JUSTIFY_CONTENT, |v: AlignContent| {
                    style.justify_content = opt_align_content_to_taffy(&v)
                }),

                // Gap
                "gap_width" => field!(F_GAP_WIDTH, |v: LengthPercentageInput| {
                    style.gap.width = v.to_taffy()
                }),
                "gap_height" => field!(F_GAP_HEIGHT, |v: LengthPercentageInput| {
                    style.gap.height = v.to_taffy()
                }),

                // Block
                "text_align" => field!(F_TEXT_ALIGN, |v: TextAlign| {
                    style.text_align = (&v).into()
                }),

                // Flexbox
                "flex_direction" => field!(F_FLEX_DIRECTION, |v: FlexDirection| {
                    style.flex_direction = (&v).into()
                }),
                "flex_wrap" => field!(F_FLEX_WRAP, |v: FlexWrap| style.flex_wrap = (&v).into()),
                "flex_basis" => field!(F_FLEX_BASIS, |v: FlexBasisInput| {
                    style.flex_basis = v.to_taffy(py)
                }),
                "flex_grow" => field!(F_FLEX_GROW, |v: f32| style.flex_grow = v),
                "flex_shrink" => field!(F_FLEX_SHRINK, |v: f32| style.flex_shrink = v),
                "flex_line_count" => field!(F_FLEX_LINE_COUNT, |v: u16| {
                    if v == 0 {
                        return Err(InvalidFlexLineCount::new_err(
                            "flex_line_count must be at least 1, got 0",
                        ));
                    }
                    style.flex_line_count = v
                }),

                // Grid
                "grid_template_rows" => {
                    field!(F_GRID_TEMPLATE_ROWS, |v: Vec<GridTemplateInput>| {
                        style.grid_template_rows = tracks_to_taffy(py, &v)
                    })
                }
                "grid_template_columns" => {
                    field!(F_GRID_TEMPLATE_COLUMNS, |v: Vec<GridTemplateInput>| {
                        style.grid_template_columns = tracks_to_taffy(py, &v)
                    })
                }
                "grid_template_row_names" => {
                    field!(F_GRID_TEMPLATE_ROW_NAMES, |v: Vec<Vec<String>>| {
                        style.grid_template_row_names = v
                    })
                }
                "grid_template_column_names" => {
                    field!(F_GRID_TEMPLATE_COLUMN_NAMES, |v: Vec<Vec<String>>| {
                        style.grid_template_column_names = v
                    })
                }
                "grid_template_areas" => {
                    opt_field!(F_GRID_TEMPLATE_AREAS, |v: GridTemplateAreas| {
                        style.grid_template_areas = v.map(|a| a.inner)
                    })
                }
                "grid_auto_rows" => field!(F_GRID_AUTO_ROWS, |v: Vec<GridTrackInput>| {
                    style.grid_auto_rows = auto_tracks_to_taffy(py, &v)
                }),
                "grid_auto_columns" => field!(F_GRID_AUTO_COLUMNS, |v: Vec<GridTrackInput>| {
                    style.grid_auto_columns = auto_tracks_to_taffy(py, &v)
                }),
                "grid_auto_flow" => field!(F_GRID_AUTO_FLOW, |v: GridAutoFlow| {
                    style.grid_auto_flow = (&v).into()
                }),
                "grid_row" => field!(F_GRID_ROW, |v: GridPlacement| style.grid_row = (&v).into()),
                "grid_column" => field!(F_GRID_COLUMN, |v: GridPlacement| {
                    style.grid_column = (&v).into()
                }),

                // Worded like pyo3's error for a keyword its own signatures don't accept.
                _ => {
                    return Err(PyTypeError::new_err(format!(
                        "Style.__new__() got an unexpected keyword argument '{name}'"
                    )))
                }
            }
        }

        Ok(Self::from_parts(style, set_fields))
    }

    /// The names of the explicitly set fields.
    #[getter]
    fn fields_set<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyFrozenSet>> {
        let names = FIELDS
            .iter()
            .filter(|(_, flag)| self.set_fields & flag != 0)
            .map(|(name, _)| *name);
        PyFrozenSet::new(py, names)
    }

    // --- Getters ---

    #[getter]
    fn get_display(&self) -> Display {
        self.inner.display.into()
    }

    #[getter]
    fn get_box_sizing(&self) -> BoxSizing {
        self.inner.box_sizing.into()
    }

    #[getter]
    fn get_overflow_x(&self) -> Overflow {
        self.inner.overflow.x.into()
    }

    #[getter]
    fn get_overflow_y(&self) -> Overflow {
        self.inner.overflow.y.into()
    }

    #[getter]
    fn get_scrollbar_width(&self) -> f32 {
        self.inner.scrollbar_width
    }

    #[getter]
    fn get_position(&self) -> Position {
        self.inner.position.into()
    }

    #[getter]
    fn get_direction(&self) -> Direction {
        self.inner.direction.into()
    }

    #[getter]
    fn get_contain(&self) -> Contain {
        self.inner.contain.into()
    }

    #[getter]
    fn get_float(&self) -> Float {
        self.inner.float.into()
    }

    #[getter]
    fn get_clear(&self) -> Clear {
        self.inner.clear.into()
    }

    #[getter]
    fn get_item_is_table(&self) -> bool {
        self.inner.item_is_table
    }

    #[getter]
    fn get_item_is_replaced(&self) -> bool {
        self.inner.item_is_replaced
    }

    // Inset
    #[getter]
    fn get_inset_left(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.inset.left)
    }
    #[getter]
    fn get_inset_right(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.inset.right)
    }
    #[getter]
    fn get_inset_top(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.inset.top)
    }
    #[getter]
    fn get_inset_bottom(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.inset.bottom)
    }

    // Size
    #[getter]
    fn get_size_width(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        dimension_to_py(py, self.inner.size.width)
    }
    #[getter]
    fn get_size_height(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        dimension_to_py(py, self.inner.size.height)
    }
    #[getter]
    fn get_min_size_width(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.min_size.width)
    }
    #[getter]
    fn get_min_size_height(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.min_size.height)
    }
    #[getter]
    fn get_max_size_width(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.max_size.width)
    }
    #[getter]
    fn get_max_size_height(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.max_size.height)
    }

    #[getter]
    fn get_aspect_ratio(&self) -> Option<f32> {
        self.inner.aspect_ratio
    }

    // Margin
    #[getter]
    fn get_margin_left(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.margin.left)
    }
    #[getter]
    fn get_margin_right(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.margin.right)
    }
    #[getter]
    fn get_margin_top(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.margin.top)
    }
    #[getter]
    fn get_margin_bottom(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_auto_to_py(py, self.inner.margin.bottom)
    }

    // Padding
    #[getter]
    fn get_padding_left(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.padding.left)
    }
    #[getter]
    fn get_padding_right(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.padding.right)
    }
    #[getter]
    fn get_padding_top(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.padding.top)
    }
    #[getter]
    fn get_padding_bottom(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.padding.bottom)
    }

    // Border
    #[getter]
    fn get_border_left(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.border.left)
    }
    #[getter]
    fn get_border_right(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.border.right)
    }
    #[getter]
    fn get_border_top(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.border.top)
    }
    #[getter]
    fn get_border_bottom(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.border.bottom)
    }

    // Alignment
    #[getter]
    fn get_align_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_items)
    }

    #[getter]
    fn get_align_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.align_self)
    }

    #[getter]
    fn get_justify_items(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_items)
    }

    #[getter]
    fn get_justify_self(&self) -> Option<AlignItems> {
        opt_align_items_from_taffy(self.inner.justify_self)
    }

    #[getter]
    fn get_align_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.align_content)
    }

    #[getter]
    fn get_justify_content(&self) -> Option<AlignContent> {
        opt_align_content_from_taffy(self.inner.justify_content)
    }

    // Gap
    #[getter]
    fn get_gap_width(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.gap.width)
    }
    #[getter]
    fn get_gap_height(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        length_percentage_to_py(py, self.inner.gap.height)
    }

    // Block
    #[getter]
    fn get_text_align(&self) -> TextAlign {
        self.inner.text_align.into()
    }

    // Flexbox
    #[getter]
    fn get_flex_direction(&self) -> FlexDirection {
        self.inner.flex_direction.into()
    }

    #[getter]
    fn get_flex_wrap(&self) -> FlexWrap {
        self.inner.flex_wrap.into()
    }

    #[getter]
    fn get_flex_basis(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        dimension_to_py(py, self.inner.flex_basis)
    }

    #[getter]
    fn get_flex_grow(&self) -> f32 {
        self.inner.flex_grow
    }

    #[getter]
    fn get_flex_shrink(&self) -> f32 {
        self.inner.flex_shrink
    }

    #[getter]
    fn get_flex_line_count(&self) -> u16 {
        self.inner.flex_line_count
    }

    // Grid
    #[getter]
    fn get_grid_template_rows(&self, py: Python<'_>) -> PyResult<Vec<Py<PyAny>>> {
        tracks_from_taffy(py, &self.inner.grid_template_rows)
    }

    #[getter]
    fn get_grid_template_columns(&self, py: Python<'_>) -> PyResult<Vec<Py<PyAny>>> {
        tracks_from_taffy(py, &self.inner.grid_template_columns)
    }

    #[getter]
    fn get_grid_template_row_names(&self) -> Vec<Vec<String>> {
        self.inner.grid_template_row_names.clone()
    }

    #[getter]
    fn get_grid_template_column_names(&self) -> Vec<Vec<String>> {
        self.inner.grid_template_column_names.clone()
    }

    #[getter]
    fn get_grid_template_areas(&self) -> Option<GridTemplateAreas> {
        self.inner
            .grid_template_areas
            .clone()
            .map(|inner| GridTemplateAreas { inner })
    }

    #[getter]
    fn get_grid_auto_rows(&self, py: Python<'_>) -> PyResult<Vec<Py<PyAny>>> {
        auto_tracks_from_taffy(py, &self.inner.grid_auto_rows)
    }

    #[getter]
    fn get_grid_auto_columns(&self, py: Python<'_>) -> PyResult<Vec<Py<PyAny>>> {
        auto_tracks_from_taffy(py, &self.inner.grid_auto_columns)
    }

    #[getter]
    fn get_grid_auto_flow(&self) -> GridAutoFlow {
        self.inner.grid_auto_flow.into()
    }

    #[getter]
    fn get_grid_row(&self) -> GridPlacement {
        self.inner.grid_row.clone().into()
    }

    #[getter]
    fn get_grid_column(&self) -> GridPlacement {
        self.inner.grid_column.clone().into()
    }

    fn __eq__(&self, other: &Style) -> bool {
        self.set_fields == other.set_fields && self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        *self.hash.get_or_init(|| self.compute_hash())
    }

    /// The set fields in declaration order, each with its getter's repr.
    fn __repr__(slf: &Bound<'_, Self>) -> PyResult<String> {
        let set_fields = slf.borrow().set_fields;
        let mut parts = Vec::new();
        for (name, flag) in FIELDS {
            if set_fields & flag != 0 {
                parts.push(format!("{name}={}", slf.getattr(*name)?.repr()?));
            }
        }
        Ok(format!("Style({})", parts.join(", ")))
    }

    /// Merge two styles: `self | other`. Fields explicitly set in `other` override
    /// those in `self`. Fields not set in `other` are preserved from `self`.
    fn __or__(&self, other: &Style) -> Style {
        let mut inner = self.to_taffy();
        copy_fields(&mut inner, &other.inner, other.set_fields);
        Style::from_parts(inner, self.set_fields | other.set_fields)
    }
}

impl From<&taffy::Style> for Style {
    fn from(s: &taffy::Style) -> Self {
        // taffy doesn't keep track of which fields were explicitly set, so mark them all set.
        Self::from_parts(s.clone(), ALL_FIELDS)
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Style>()?;
    Ok(())
}
