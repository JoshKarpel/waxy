use pyo3::prelude::*;

/// How the node should be displayed.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum Display {
    Block = 0,
    Flex = 1,
    Grid = 2,
    #[pyo3(name = "Nil")]
    None = 3,
}

impl From<taffy::Display> for Display {
    fn from(d: taffy::Display) -> Self {
        match d {
            taffy::Display::Block => Display::Block,
            taffy::Display::Flex => Display::Flex,
            taffy::Display::Grid => Display::Grid,
            taffy::Display::None => Display::None,
        }
    }
}

impl From<&Display> for taffy::Display {
    fn from(d: &Display) -> Self {
        match d {
            Display::Block => taffy::Display::Block,
            Display::Flex => taffy::Display::Flex,
            Display::Grid => taffy::Display::Grid,
            Display::None => taffy::Display::None,
        }
    }
}

/// How the node should be positioned.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum Position {
    Relative = 0,
    Absolute = 1,
}

impl From<taffy::Position> for Position {
    fn from(p: taffy::Position) -> Self {
        match p {
            taffy::Position::Relative => Position::Relative,
            taffy::Position::Absolute => Position::Absolute,
        }
    }
}

impl From<&Position> for taffy::Position {
    fn from(p: &Position) -> Self {
        match p {
            Position::Relative => taffy::Position::Relative,
            Position::Absolute => taffy::Position::Absolute,
        }
    }
}

/// The direction of a flex container's main axis.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum FlexDirection {
    Row = 0,
    Column = 1,
    RowReverse = 2,
    ColumnReverse = 3,
}

impl From<taffy::FlexDirection> for FlexDirection {
    fn from(d: taffy::FlexDirection) -> Self {
        match d {
            taffy::FlexDirection::Row => FlexDirection::Row,
            taffy::FlexDirection::Column => FlexDirection::Column,
            taffy::FlexDirection::RowReverse => FlexDirection::RowReverse,
            taffy::FlexDirection::ColumnReverse => FlexDirection::ColumnReverse,
        }
    }
}

impl From<&FlexDirection> for taffy::FlexDirection {
    fn from(d: &FlexDirection) -> Self {
        match d {
            FlexDirection::Row => taffy::FlexDirection::Row,
            FlexDirection::Column => taffy::FlexDirection::Column,
            FlexDirection::RowReverse => taffy::FlexDirection::RowReverse,
            FlexDirection::ColumnReverse => taffy::FlexDirection::ColumnReverse,
        }
    }
}

/// Whether flex items wrap.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum FlexWrap {
    NoWrap = 0,
    Wrap = 1,
    WrapReverse = 2,
}

impl From<taffy::FlexWrap> for FlexWrap {
    fn from(w: taffy::FlexWrap) -> Self {
        match w {
            taffy::FlexWrap::NoWrap => FlexWrap::NoWrap,
            taffy::FlexWrap::Wrap => FlexWrap::Wrap,
            taffy::FlexWrap::WrapReverse => FlexWrap::WrapReverse,
        }
    }
}

impl From<&FlexWrap> for taffy::FlexWrap {
    fn from(w: &FlexWrap) -> Self {
        match w {
            FlexWrap::NoWrap => taffy::FlexWrap::NoWrap,
            FlexWrap::Wrap => taffy::FlexWrap::Wrap,
            FlexWrap::WrapReverse => taffy::FlexWrap::WrapReverse,
        }
    }
}

/// Alignment of items along the cross axis.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum AlignItems {
    Start = 0,
    End = 1,
    FlexStart = 2,
    FlexEnd = 3,
    Center = 4,
    Baseline = 5,
    Stretch = 6,
}

impl From<taffy::AlignItems> for AlignItems {
    fn from(a: taffy::AlignItems) -> Self {
        match a {
            taffy::AlignItems::Start => AlignItems::Start,
            taffy::AlignItems::End => AlignItems::End,
            taffy::AlignItems::FlexStart => AlignItems::FlexStart,
            taffy::AlignItems::FlexEnd => AlignItems::FlexEnd,
            taffy::AlignItems::Center => AlignItems::Center,
            taffy::AlignItems::Baseline => AlignItems::Baseline,
            taffy::AlignItems::Stretch => AlignItems::Stretch,
        }
    }
}

impl From<&AlignItems> for taffy::AlignItems {
    fn from(a: &AlignItems) -> Self {
        match a {
            AlignItems::Start => taffy::AlignItems::Start,
            AlignItems::End => taffy::AlignItems::End,
            AlignItems::FlexStart => taffy::AlignItems::FlexStart,
            AlignItems::FlexEnd => taffy::AlignItems::FlexEnd,
            AlignItems::Center => taffy::AlignItems::Center,
            AlignItems::Baseline => taffy::AlignItems::Baseline,
            AlignItems::Stretch => taffy::AlignItems::Stretch,
        }
    }
}

/// Alignment of content within the container.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum AlignContent {
    Start = 0,
    End = 1,
    FlexStart = 2,
    FlexEnd = 3,
    Center = 4,
    Stretch = 5,
    SpaceBetween = 6,
    SpaceEvenly = 7,
    SpaceAround = 8,
}

impl From<taffy::AlignContent> for AlignContent {
    fn from(a: taffy::AlignContent) -> Self {
        match a {
            taffy::AlignContent::Start => AlignContent::Start,
            taffy::AlignContent::End => AlignContent::End,
            taffy::AlignContent::FlexStart => AlignContent::FlexStart,
            taffy::AlignContent::FlexEnd => AlignContent::FlexEnd,
            taffy::AlignContent::Center => AlignContent::Center,
            taffy::AlignContent::Stretch => AlignContent::Stretch,
            taffy::AlignContent::SpaceBetween => AlignContent::SpaceBetween,
            taffy::AlignContent::SpaceEvenly => AlignContent::SpaceEvenly,
            taffy::AlignContent::SpaceAround => AlignContent::SpaceAround,
        }
    }
}

impl From<&AlignContent> for taffy::AlignContent {
    fn from(a: &AlignContent) -> Self {
        match a {
            AlignContent::Start => taffy::AlignContent::Start,
            AlignContent::End => taffy::AlignContent::End,
            AlignContent::FlexStart => taffy::AlignContent::FlexStart,
            AlignContent::FlexEnd => taffy::AlignContent::FlexEnd,
            AlignContent::Center => taffy::AlignContent::Center,
            AlignContent::Stretch => taffy::AlignContent::Stretch,
            AlignContent::SpaceBetween => taffy::AlignContent::SpaceBetween,
            AlignContent::SpaceEvenly => taffy::AlignContent::SpaceEvenly,
            AlignContent::SpaceAround => taffy::AlignContent::SpaceAround,
        }
    }
}

/// How content overflows its container.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum Overflow {
    Visible = 0,
    Clip = 1,
    Hidden = 2,
    Scroll = 3,
}

impl From<taffy::Overflow> for Overflow {
    fn from(o: taffy::Overflow) -> Self {
        match o {
            taffy::Overflow::Visible => Overflow::Visible,
            taffy::Overflow::Clip => Overflow::Clip,
            taffy::Overflow::Hidden => Overflow::Hidden,
            taffy::Overflow::Scroll => Overflow::Scroll,
        }
    }
}

impl From<&Overflow> for taffy::Overflow {
    fn from(o: &Overflow) -> Self {
        match o {
            Overflow::Visible => taffy::Overflow::Visible,
            Overflow::Clip => taffy::Overflow::Clip,
            Overflow::Hidden => taffy::Overflow::Hidden,
            Overflow::Scroll => taffy::Overflow::Scroll,
        }
    }
}

/// How grid items are auto-placed.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum GridAutoFlow {
    Row = 0,
    Column = 1,
    RowDense = 2,
    ColumnDense = 3,
}

impl From<taffy::GridAutoFlow> for GridAutoFlow {
    fn from(g: taffy::GridAutoFlow) -> Self {
        match g {
            taffy::GridAutoFlow::Row => GridAutoFlow::Row,
            taffy::GridAutoFlow::Column => GridAutoFlow::Column,
            taffy::GridAutoFlow::RowDense => GridAutoFlow::RowDense,
            taffy::GridAutoFlow::ColumnDense => GridAutoFlow::ColumnDense,
        }
    }
}

impl From<&GridAutoFlow> for taffy::GridAutoFlow {
    fn from(g: &GridAutoFlow) -> Self {
        match g {
            GridAutoFlow::Row => taffy::GridAutoFlow::Row,
            GridAutoFlow::Column => taffy::GridAutoFlow::Column,
            GridAutoFlow::RowDense => taffy::GridAutoFlow::RowDense,
            GridAutoFlow::ColumnDense => taffy::GridAutoFlow::ColumnDense,
        }
    }
}

/// Box sizing model.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum BoxSizing {
    BorderBox = 0,
    ContentBox = 1,
}

impl From<taffy::BoxSizing> for BoxSizing {
    fn from(b: taffy::BoxSizing) -> Self {
        match b {
            taffy::BoxSizing::BorderBox => BoxSizing::BorderBox,
            taffy::BoxSizing::ContentBox => BoxSizing::ContentBox,
        }
    }
}

impl From<&BoxSizing> for taffy::BoxSizing {
    fn from(b: &BoxSizing) -> Self {
        match b {
            BoxSizing::BorderBox => taffy::BoxSizing::BorderBox,
            BoxSizing::ContentBox => taffy::BoxSizing::ContentBox,
        }
    }
}

/// Text alignment.
#[pyclass(eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum TextAlign {
    Auto = 0,
    LegacyLeft = 1,
    LegacyRight = 2,
    LegacyCenter = 3,
}

impl From<taffy::TextAlign> for TextAlign {
    fn from(t: taffy::TextAlign) -> Self {
        match t {
            taffy::TextAlign::Auto => TextAlign::Auto,
            taffy::TextAlign::LegacyLeft => TextAlign::LegacyLeft,
            taffy::TextAlign::LegacyRight => TextAlign::LegacyRight,
            taffy::TextAlign::LegacyCenter => TextAlign::LegacyCenter,
        }
    }
}

impl From<&TextAlign> for taffy::TextAlign {
    fn from(t: &TextAlign) -> Self {
        match t {
            TextAlign::Auto => taffy::TextAlign::Auto,
            TextAlign::LegacyLeft => taffy::TextAlign::LegacyLeft,
            TextAlign::LegacyRight => taffy::TextAlign::LegacyRight,
            TextAlign::LegacyCenter => taffy::TextAlign::LegacyCenter,
        }
    }
}

/// Available space for layout.
#[pyclass(unsendable)]
#[derive(Clone, Debug)]
pub struct AvailableSpace {
    inner: taffy::AvailableSpace,
}

#[pymethods]
impl AvailableSpace {
    /// Create a definite available space.
    #[staticmethod]
    fn definite(value: f32) -> Self {
        Self {
            inner: taffy::AvailableSpace::Definite(value),
        }
    }

    /// Create a min-content available space.
    #[staticmethod]
    fn min_content() -> Self {
        Self {
            inner: taffy::AvailableSpace::MinContent,
        }
    }

    /// Create a max-content available space.
    #[staticmethod]
    fn max_content() -> Self {
        Self {
            inner: taffy::AvailableSpace::MaxContent,
        }
    }

    fn is_definite(&self) -> bool {
        self.inner.is_definite()
    }

    fn __repr__(&self) -> String {
        match self.inner {
            taffy::AvailableSpace::Definite(v) => format!("AvailableSpace.definite({v})"),
            taffy::AvailableSpace::MinContent => "AvailableSpace.min_content()".to_string(),
            taffy::AvailableSpace::MaxContent => "AvailableSpace.max_content()".to_string(),
        }
    }
}

impl From<taffy::AvailableSpace> for AvailableSpace {
    fn from(a: taffy::AvailableSpace) -> Self {
        Self { inner: a }
    }
}

impl From<&AvailableSpace> for taffy::AvailableSpace {
    fn from(a: &AvailableSpace) -> Self {
        a.inner
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Display>()?;
    m.add_class::<Position>()?;
    m.add_class::<FlexDirection>()?;
    m.add_class::<FlexWrap>()?;
    m.add_class::<AlignItems>()?;
    m.add_class::<AlignContent>()?;
    m.add_class::<Overflow>()?;
    m.add_class::<GridAutoFlow>()?;
    m.add_class::<BoxSizing>()?;
    m.add_class::<TextAlign>()?;
    m.add_class::<AvailableSpace>()?;
    Ok(())
}
