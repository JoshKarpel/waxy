use pyo3::prelude::*;

/// How the node should be displayed.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum Display {
    Block = 0,
    Flex = 1,
    Grid = 2,
    #[pyo3(name = "Nil")]
    None = 3,
    FlowRoot = 4,
}

impl From<taffy::Display> for Display {
    fn from(d: taffy::Display) -> Self {
        match d {
            taffy::Display::Block => Display::Block,
            taffy::Display::Flex => Display::Flex,
            taffy::Display::Grid => Display::Grid,
            taffy::Display::None => Display::None,
            taffy::Display::FlowRoot => Display::FlowRoot,
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
            Display::FlowRoot => taffy::Display::FlowRoot,
        }
    }
}

/// How the node should be positioned.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum FlexWrap {
    NoWrap = 0,
    Wrap = 1,
    WrapReverse = 2,
    Balance = 3,
    BalanceReverse = 4,
}

impl From<taffy::FlexWrap> for FlexWrap {
    fn from(w: taffy::FlexWrap) -> Self {
        match w {
            taffy::FlexWrap::NoWrap => FlexWrap::NoWrap,
            taffy::FlexWrap::Wrap => FlexWrap::Wrap,
            taffy::FlexWrap::WrapReverse => FlexWrap::WrapReverse,
            taffy::FlexWrap::Balance => FlexWrap::Balance,
            taffy::FlexWrap::BalanceReverse => FlexWrap::BalanceReverse,
        }
    }
}

impl From<&FlexWrap> for taffy::FlexWrap {
    fn from(w: &FlexWrap) -> Self {
        match w {
            FlexWrap::NoWrap => taffy::FlexWrap::NoWrap,
            FlexWrap::Wrap => taffy::FlexWrap::Wrap,
            FlexWrap::WrapReverse => taffy::FlexWrap::WrapReverse,
            FlexWrap::Balance => taffy::FlexWrap::Balance,
            FlexWrap::BalanceReverse => taffy::FlexWrap::BalanceReverse,
        }
    }
}

/// Alignment of items along the cross axis.
///
/// The `Safe*` members are the `safe` overflow-position variants: an item that would
/// overflow its alignment container is aligned as if `Start` instead.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum AlignItems {
    Start = 0,
    End = 1,
    FlexStart = 2,
    FlexEnd = 3,
    Center = 4,
    Baseline = 5,
    Stretch = 6,
    SelfStart = 7,
    SelfEnd = 8,
    SafeStart = 9,
    SafeEnd = 10,
    SafeFlexStart = 11,
    SafeFlexEnd = 12,
    SafeCenter = 13,
    SafeSelfStart = 14,
    SafeSelfEnd = 15,
}

impl From<taffy::AlignItems> for AlignItems {
    fn from(a: taffy::AlignItems) -> Self {
        use taffy::style::AlignItemsKeyword as K;
        use taffy::style::AlignmentSafety as S;
        match (a.keyword, a.safety) {
            (K::Start, S::Unsafe) => AlignItems::Start,
            (K::End, S::Unsafe) => AlignItems::End,
            (K::FlexStart, S::Unsafe) => AlignItems::FlexStart,
            (K::FlexEnd, S::Unsafe) => AlignItems::FlexEnd,
            (K::Center, S::Unsafe) => AlignItems::Center,
            (K::Baseline, S::Unsafe) => AlignItems::Baseline,
            (K::Stretch, S::Unsafe) => AlignItems::Stretch,
            (K::SelfStart, S::Unsafe) => AlignItems::SelfStart,
            (K::SelfEnd, S::Unsafe) => AlignItems::SelfEnd,
            (K::Start, S::Safe) => AlignItems::SafeStart,
            (K::End, S::Safe) => AlignItems::SafeEnd,
            (K::FlexStart, S::Safe) => AlignItems::SafeFlexStart,
            (K::FlexEnd, S::Safe) => AlignItems::SafeFlexEnd,
            (K::Center, S::Safe) => AlignItems::SafeCenter,
            (K::SelfStart, S::Safe) => AlignItems::SafeSelfStart,
            (K::SelfEnd, S::Safe) => AlignItems::SafeSelfEnd,
            // CSS has no `safe baseline` or `safe stretch` (taffy has no constant for them),
            // and only waxy writes these fields.
            (K::Baseline | K::Stretch, S::Safe) => {
                unreachable!("waxy never constructs safe {:?} alignment", a.keyword)
            }
        }
    }
}

impl From<&AlignItems> for taffy::AlignItems {
    fn from(a: &AlignItems) -> Self {
        match a {
            AlignItems::Start => taffy::AlignItems::START,
            AlignItems::End => taffy::AlignItems::END,
            AlignItems::FlexStart => taffy::AlignItems::FLEX_START,
            AlignItems::FlexEnd => taffy::AlignItems::FLEX_END,
            AlignItems::Center => taffy::AlignItems::CENTER,
            AlignItems::Baseline => taffy::AlignItems::BASELINE,
            AlignItems::Stretch => taffy::AlignItems::STRETCH,
            AlignItems::SelfStart => taffy::AlignItems::SELF_START,
            AlignItems::SelfEnd => taffy::AlignItems::SELF_END,
            AlignItems::SafeStart => taffy::AlignItems::SAFE_START,
            AlignItems::SafeEnd => taffy::AlignItems::SAFE_END,
            AlignItems::SafeFlexStart => taffy::AlignItems::SAFE_FLEX_START,
            AlignItems::SafeFlexEnd => taffy::AlignItems::SAFE_FLEX_END,
            AlignItems::SafeCenter => taffy::AlignItems::SAFE_CENTER,
            AlignItems::SafeSelfStart => taffy::AlignItems::SAFE_SELF_START,
            AlignItems::SafeSelfEnd => taffy::AlignItems::SAFE_SELF_END,
        }
    }
}

/// Alignment of content within the container.
///
/// The `Safe*` members are the `safe` overflow-position variants: content that would
/// overflow the container is aligned as if `Start` instead.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
    SafeStart = 9,
    SafeEnd = 10,
    SafeFlexStart = 11,
    SafeFlexEnd = 12,
    SafeCenter = 13,
}

impl From<taffy::AlignContent> for AlignContent {
    fn from(a: taffy::AlignContent) -> Self {
        use taffy::style::AlignContentKeyword as K;
        use taffy::style::AlignmentSafety as S;
        match (a.keyword, a.safety) {
            (K::Start, S::Unsafe) => AlignContent::Start,
            (K::End, S::Unsafe) => AlignContent::End,
            (K::FlexStart, S::Unsafe) => AlignContent::FlexStart,
            (K::FlexEnd, S::Unsafe) => AlignContent::FlexEnd,
            (K::Center, S::Unsafe) => AlignContent::Center,
            (K::Stretch, S::Unsafe) => AlignContent::Stretch,
            (K::SpaceBetween, S::Unsafe) => AlignContent::SpaceBetween,
            (K::SpaceEvenly, S::Unsafe) => AlignContent::SpaceEvenly,
            (K::SpaceAround, S::Unsafe) => AlignContent::SpaceAround,
            (K::Start, S::Safe) => AlignContent::SafeStart,
            (K::End, S::Safe) => AlignContent::SafeEnd,
            (K::FlexStart, S::Safe) => AlignContent::SafeFlexStart,
            (K::FlexEnd, S::Safe) => AlignContent::SafeFlexEnd,
            (K::Center, S::Safe) => AlignContent::SafeCenter,
            // CSS has no safe distributed alignment (taffy has no constant for it), and only
            // waxy writes these fields.
            (K::Stretch | K::SpaceBetween | K::SpaceEvenly | K::SpaceAround, S::Safe) => {
                unreachable!("waxy never constructs safe {:?} alignment", a.keyword)
            }
        }
    }
}

impl From<&AlignContent> for taffy::AlignContent {
    fn from(a: &AlignContent) -> Self {
        match a {
            AlignContent::Start => taffy::AlignContent::START,
            AlignContent::End => taffy::AlignContent::END,
            AlignContent::FlexStart => taffy::AlignContent::FLEX_START,
            AlignContent::FlexEnd => taffy::AlignContent::FLEX_END,
            AlignContent::Center => taffy::AlignContent::CENTER,
            AlignContent::Stretch => taffy::AlignContent::STRETCH,
            AlignContent::SpaceBetween => taffy::AlignContent::SPACE_BETWEEN,
            AlignContent::SpaceEvenly => taffy::AlignContent::SPACE_EVENLY,
            AlignContent::SpaceAround => taffy::AlignContent::SPACE_AROUND,
            AlignContent::SafeStart => taffy::AlignContent::SAFE_START,
            AlignContent::SafeEnd => taffy::AlignContent::SAFE_END,
            AlignContent::SafeFlexStart => taffy::AlignContent::SAFE_FLEX_START,
            AlignContent::SafeFlexEnd => taffy::AlignContent::SAFE_FLEX_END,
            AlignContent::SafeCenter => taffy::AlignContent::SAFE_CENTER,
        }
    }
}

/// How content overflows its container.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
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

/// The inline direction of a node's content (CSS `direction`).
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum Direction {
    Ltr = 0,
    Rtl = 1,
}

impl From<taffy::Direction> for Direction {
    fn from(d: taffy::Direction) -> Self {
        match d {
            taffy::Direction::Ltr => Direction::Ltr,
            taffy::Direction::Rtl => Direction::Rtl,
        }
    }
}

impl From<&Direction> for taffy::Direction {
    fn from(d: &Direction) -> Self {
        match d {
            Direction::Ltr => taffy::Direction::Ltr,
            Direction::Rtl => taffy::Direction::Rtl,
        }
    }
}

/// Which side a node floats to within a block container (CSS `float`).
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum Float {
    Left = 0,
    Right = 1,
    #[pyo3(name = "Nil")]
    None = 2,
}

impl From<taffy::Float> for Float {
    fn from(f: taffy::Float) -> Self {
        match f {
            taffy::Float::Left => Float::Left,
            taffy::Float::Right => Float::Right,
            taffy::Float::None => Float::None,
        }
    }
}

impl From<&Float> for taffy::Float {
    fn from(f: &Float) -> Self {
        match f {
            Float::Left => taffy::Float::Left,
            Float::Right => taffy::Float::Right,
            Float::None => taffy::Float::None,
        }
    }
}

/// Which preceding floats a node is moved below (CSS `clear`).
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum Clear {
    Left = 0,
    Right = 1,
    Both = 2,
    #[pyo3(name = "Nil")]
    None = 3,
}

impl From<taffy::Clear> for Clear {
    fn from(c: taffy::Clear) -> Self {
        match c {
            taffy::Clear::Left => Clear::Left,
            taffy::Clear::Right => Clear::Right,
            taffy::Clear::Both => Clear::Both,
            taffy::Clear::None => Clear::None,
        }
    }
}

impl From<&Clear> for taffy::Clear {
    fn from(c: &Clear) -> Self {
        match c {
            Clear::Left => taffy::Clear::Left,
            Clear::Right => taffy::Clear::Right,
            Clear::Both => taffy::Clear::Both,
            Clear::None => taffy::Clear::None,
        }
    }
}

/// CSS containment (`contain`). Taffy supports the `layout` and `paint` containment types;
/// `Content` is both.
#[pyclass(eq, eq_int, from_py_object, module = "waxy")]
#[derive(Clone, Debug, PartialEq)]
pub enum Contain {
    #[pyo3(name = "Nil")]
    None = 0,
    Layout = 1,
    Paint = 2,
    Content = 3,
}

impl From<taffy::Contain> for Contain {
    fn from(c: taffy::Contain) -> Self {
        // taffy's Contain is a two-bit set, so these four cases are all of its values.
        match (
            c.contains(taffy::Contain::LAYOUT),
            c.contains(taffy::Contain::PAINT),
        ) {
            (false, false) => Contain::None,
            (true, false) => Contain::Layout,
            (false, true) => Contain::Paint,
            (true, true) => Contain::Content,
        }
    }
}

impl From<&Contain> for taffy::Contain {
    fn from(c: &Contain) -> Self {
        match c {
            Contain::None => taffy::Contain::NONE,
            Contain::Layout => taffy::Contain::LAYOUT,
            Contain::Paint => taffy::Contain::PAINT,
            Contain::Content => taffy::Contain::CONTENT,
        }
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
    m.add_class::<Direction>()?;
    m.add_class::<Float>()?;
    m.add_class::<Clear>()?;
    m.add_class::<Contain>()?;
    Ok(())
}
