from collections.abc import Callable, Iterator

# Exceptions

class WaxyException(Exception):
    """Base exception for all waxy errors."""

class TaffyException(WaxyException):
    """Base exception for all taffy errors."""

class InvalidPercent(WaxyException, ValueError):
    """Raised when Percent(value) is called with a value outside [0.0, 1.0]."""

class ChildIndexOutOfBounds(TaffyException):
    """Child index is out of bounds."""

class InvalidParentNode(TaffyException):
    """Parent node is invalid."""

class InvalidChildNode(TaffyException):
    """Child node is invalid."""

class InvalidInputNode(TaffyException):
    """Input node is invalid."""

# Geometry

class Size:
    """A 2D size with width and height."""

    def __init__(self, width: float = 0.0, height: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...
    @property
    def area(self) -> float:
        """The area (width * height)."""

class Rect:
    """A rectangle with left, right, top, bottom edges."""

    def __init__(
        self,
        left: float = 0.0,
        right: float = 0.0,
        top: float = 0.0,
        bottom: float = 0.0,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __iter__(self) -> Iterator[Point]: ...
    def __len__(self) -> int: ...
    @property
    def left(self) -> float: ...
    @property
    def right(self) -> float: ...
    @property
    def top(self) -> float: ...
    @property
    def bottom(self) -> float: ...
    @property
    def width(self) -> float:
        """The width of the rectangle (right - left)."""
    @property
    def height(self) -> float:
        """The height of the rectangle (bottom - top)."""
    @property
    def size(self) -> Size:
        """The size of the rectangle as a Size."""
    def contains(self, point: Point) -> bool:
        """Check if a point is inside this rectangle."""
    @property
    def top_left(self) -> Point:
        """The top-left corner point."""
    @property
    def top_right(self) -> Point:
        """The top-right corner point."""
    @property
    def bottom_right(self) -> Point:
        """The bottom-right corner point."""
    @property
    def bottom_left(self) -> Point:
        """The bottom-left corner point."""
    def corners(self) -> tuple[Point, Point, Point, Point]:
        """Return the four corner points (top-left, top-right, bottom-right, bottom-left)."""
    def top_edge(self) -> Iterator[Point]:
        """Iterate over integer pixel locations along the top edge."""
    def bottom_edge(self) -> Iterator[Point]:
        """Iterate over integer pixel locations along the bottom edge."""
    def left_edge(self) -> Iterator[Point]:
        """Iterate over integer pixel locations along the left edge."""
    def right_edge(self) -> Iterator[Point]:
        """Iterate over integer pixel locations along the right edge."""

class Point:
    """A 2D point with x and y coordinates."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __add__(self, other: Point) -> Point: ...
    def __sub__(self, other: Point) -> Point: ...
    def __mul__(self, scalar: float) -> Point: ...
    def __rmul__(self, scalar: float) -> Point: ...
    def __truediv__(self, scalar: float) -> Point: ...
    def __neg__(self) -> Point: ...
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

class Line:
    """A line segment with start and end values."""

    def __init__(self, start: float = 0.0, end: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __iter__(self) -> Iterator[float]: ...
    def __len__(self) -> int: ...
    @property
    def start(self) -> float: ...
    @property
    def end(self) -> float: ...
    @property
    def length(self) -> float:
        """The length of the line segment (end - start)."""
    def contains(self, value: float) -> bool:
        """Check if a value is contained within this line segment."""

class KnownSize:
    """
    Known dimensions passed to measure functions (independently-optional width/height).

    Passed to the measure callback to indicate which dimensions are already known
    from the node's style. If a dimension is None, the measure function must compute it.

    See: [taffy `Size<Option<f32>>`](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Size.html)
    """

    def __init__(self, width: float | None = None, height: float | None = None) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[float | None]: ...
    @property
    def width(self) -> float | None: ...
    @property
    def height(self) -> float | None: ...

type AvailableSpaceValue = Definite | MinContent | MaxContent

class AvailableSize:
    """
    Available space for measure functions (width/height: Definite | MinContent | MaxContent).

    Passed to the measure callback to indicate how much space is available for layout.
    Each dimension is one of the available-space variants.

    See: [taffy `Size<AvailableSpace>`](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Size.html)
    """

    def __init__(
        self,
        width: AvailableSpaceValue,
        height: AvailableSpaceValue,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[AvailableSpaceValue]: ...
    @property
    def width(self) -> AvailableSpaceValue: ...
    @property
    def height(self) -> AvailableSpaceValue: ...

# Value types

class Length:
    """
    A length value in pixels.

    Used for size, padding, border, gap, margin, inset, and grid track sizing fields.

    See: [taffy `Dimension::Length`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html),
    [MDN `<length>`](https://developer.mozilla.org/en-US/docs/Web/CSS/length)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float: ...

class Percent:
    """
    A percentage value (0.0 to 1.0).

    Used for size, padding, border, gap, margin, inset, and grid track sizing fields.
    Raises InvalidPercent (a subclass of both WaxyException and ValueError) if value
    is outside the range [0.0, 1.0].

    See: [taffy `Dimension::Percent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html),
    [MDN `<percentage>`](https://developer.mozilla.org/en-US/docs/Web/CSS/percentage)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float: ...

class Auto:
    """
    Automatic sizing or placement.

    Used for size, margin, inset, flex-basis, and grid placement fields.

    See: [taffy `Dimension::Auto`](https://docs.rs/taffy/0.9.2/taffy/style/enum.Dimension.html)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class MinContent:
    """
    CSS min-content intrinsic sizing.

    The smallest size that can fit the item's contents with all soft line-wrapping
    opportunities taken. Used in available space (measure functions) and grid track sizing.

    See: [taffy `MinTrackSizingFunction::MinContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html),
    [MDN `min-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/min-content)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class MaxContent:
    """
    CSS max-content intrinsic sizing.

    The smallest size that can fit the item's contents with no soft line-wrapping
    opportunities taken. Used in available space (measure functions) and grid track sizing.

    See: [taffy `MinTrackSizingFunction::MaxContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MinTrackSizingFunction.html),
    [MDN `max-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/max-content)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

AUTO: Auto
"""Module-level Auto singleton. Equivalent to Auto() but avoids repeated construction."""

MIN_CONTENT: MinContent
"""Module-level MinContent singleton. Equivalent to MinContent() but avoids repeated construction.
"""

MAX_CONTENT: MaxContent
"""Module-level MaxContent singleton. Equivalent to MaxContent() but avoids repeated construction.
"""

class Definite:
    """
    A definite available space in pixels.

    Used only in AvailableSize (measure function input) to represent a concrete
    pixel measurement of available space.

    See: [taffy `AvailableSpace::Definite`](https://docs.rs/taffy/0.9.2/taffy/style/enum.AvailableSpace.html)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float: ...

class Fraction:
    """
    A fractional unit of remaining grid space (CSS fr unit).

    After fixed lengths and percentages are allocated, remaining space is divided
    among fractional tracks proportionally. For example, Fraction(1) and Fraction(2)
    in the same grid get 1/3 and 2/3 of remaining space.

    Used only in grid track sizing (grid_template_*, grid_auto_*).

    See: [taffy `MaxTrackSizingFunction::Fraction`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html),
    [MDN `<flex>` (fr unit)](https://developer.mozilla.org/en-US/docs/Web/CSS/flex_value)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float: ...

type GridTrackMinValue = Length | Percent | Auto | MinContent | MaxContent
type GridTrackMaxValue = Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent
type GridTrackValue = (
    Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent
)

class FitContent:
    """
    CSS fit-content() grid track sizing function.

    Grows up to a specified limit, then clamps: max(min_content, min(max_content, limit)).
    The limit must be a Length or Percent.

    Used only in grid track sizing.

    See: [taffy `MaxTrackSizingFunction::FitContent`](https://docs.rs/taffy/0.9.2/taffy/style/enum.MaxTrackSizingFunction.html),
    [MDN `fit-content()`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content_function)
    """

    __match_args__ = ("limit",)

    def __init__(self, limit: Length | Percent) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def limit(self) -> Length | Percent: ...

class Minmax:
    """
    CSS minmax() grid track sizing function.

    Defines a size range: min sets the minimum track size, max sets the maximum.

    - min: Length | Percent | Auto | MinContent | MaxContent
    - max: Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent

    Used only in grid track sizing.

    See: [taffy `TrackSizingFunction`](https://docs.rs/taffy/0.9.2/taffy/style/enum.TrackSizingFunction.html),
    [MDN `minmax()`](https://developer.mozilla.org/en-US/docs/Web/CSS/minmax)
    """

    __match_args__ = ("min", "max")

    def __init__(self, min: GridTrackMinValue, max: GridTrackMaxValue) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def min(self) -> GridTrackMinValue: ...
    @property
    def max(self) -> GridTrackMaxValue: ...

class GridLine:
    """
    A 1-based grid line index (negative indices count from the end).

    Used in GridPlacement.start and GridPlacement.end.

    See: [taffy `GridPlacement::Line`](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html),
    [MDN Line-based placement](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_line-based_placement)
    """

    __match_args__ = ("index",)

    def __init__(self, index: int) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def index(self) -> int: ...

class GridSpan:
    """
    Span a number of grid tracks.

    Used in GridPlacement.start and GridPlacement.end.

    See: [taffy `GridPlacement::Span`](https://docs.rs/taffy/0.9.2/taffy/style/enum.GridPlacement.html),
    [MDN `grid-column-start` (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column-start)
    """

    __match_args__ = ("count",)

    def __init__(self, count: int) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def count(self) -> int: ...

# Enums

class Display:
    """How the node should be displayed."""

    Block: Display
    Flex: Display
    Grid: Display
    Nil: Display

class Position:
    """How the node should be positioned."""

    Relative: Position
    Absolute: Position

class FlexDirection:
    """The direction of a flex container's main axis."""

    Row: FlexDirection
    Column: FlexDirection
    RowReverse: FlexDirection
    ColumnReverse: FlexDirection

class FlexWrap:
    """Whether flex items wrap."""

    NoWrap: FlexWrap
    Wrap: FlexWrap
    WrapReverse: FlexWrap

class AlignItems:
    """Alignment of items along the cross axis."""

    Start: AlignItems
    End: AlignItems
    FlexStart: AlignItems
    FlexEnd: AlignItems
    Center: AlignItems
    Baseline: AlignItems
    Stretch: AlignItems

class AlignContent:
    """Alignment of content within the container."""

    Start: AlignContent
    End: AlignContent
    FlexStart: AlignContent
    FlexEnd: AlignContent
    Center: AlignContent
    Stretch: AlignContent
    SpaceBetween: AlignContent
    SpaceEvenly: AlignContent
    SpaceAround: AlignContent

class Overflow:
    """How content overflows its container."""

    Visible: Overflow
    Clip: Overflow
    Hidden: Overflow
    Scroll: Overflow

class GridAutoFlow:
    """How grid items are auto-placed."""

    Row: GridAutoFlow
    Column: GridAutoFlow
    RowDense: GridAutoFlow
    ColumnDense: GridAutoFlow

class BoxSizing:
    """Box sizing model."""

    BorderBox: BoxSizing
    ContentBox: BoxSizing

class TextAlign:
    """Text alignment."""

    Auto: TextAlign
    LegacyLeft: TextAlign
    LegacyRight: TextAlign
    LegacyCenter: TextAlign

# Grid

type GridPlacementValue = GridLine | GridSpan | Auto

class GridPlacement:
    """
    A start/end pair of grid placements for a child item.

    Each of start and end is a GridLine | GridSpan | Auto value.
    Defaults both to Auto (the CSS default for unplaced items).

    See: [taffy `Line<GridPlacement>`](https://docs.rs/taffy/0.9.2/taffy/geometry/struct.Line.html),
    [MDN `grid-row`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row),
    [MDN `grid-column`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)
    """

    def __init__(
        self,
        start: GridPlacementValue | None = None,
        end: GridPlacementValue | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def start(self) -> GridPlacementValue: ...
    @property
    def end(self) -> GridPlacementValue: ...

# Node

class NodeId:
    """A handle to a node in the layout tree."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

# Layout

class Layout:
    """The computed layout of a node."""

    def __repr__(self) -> str: ...
    @property
    def order(self) -> int: ...
    @property
    def location(self) -> Point: ...
    @property
    def size(self) -> Size: ...
    @property
    def content_size(self) -> Size: ...
    @property
    def scrollbar_size(self) -> Size: ...
    @property
    def border(self) -> Rect: ...
    @property
    def padding(self) -> Rect: ...
    @property
    def margin(self) -> Rect: ...
    def content_box_width(self) -> float:
        """Width of the content box (size minus padding and border)."""
    def content_box_height(self) -> float:
        """Height of the content box (size minus padding and border)."""

# Style

type DimensionValue = Length | Percent | Auto
type LengthPercentageValue = Length | Percent

class Style:
    """
    Style properties for a layout node.

    All fields are keyword-only. Passing None (or omitting) uses the taffy default.
    Style is immutable — construct a new instance to change fields, or use | to merge.

    See: [taffy `Style`](https://docs.rs/taffy/0.9.2/taffy/struct.Style.html)
    """

    def __init__(
        self,
        *,
        display: Display | None = None,
        box_sizing: BoxSizing | None = None,
        overflow_x: Overflow | None = None,
        overflow_y: Overflow | None = None,
        scrollbar_width: float | None = None,
        position: Position | None = None,
        inset_left: DimensionValue | None = None,
        inset_right: DimensionValue | None = None,
        inset_top: DimensionValue | None = None,
        inset_bottom: DimensionValue | None = None,
        size_width: DimensionValue | None = None,
        size_height: DimensionValue | None = None,
        min_size_width: DimensionValue | None = None,
        min_size_height: DimensionValue | None = None,
        max_size_width: DimensionValue | None = None,
        max_size_height: DimensionValue | None = None,
        aspect_ratio: float | None = None,
        margin_left: DimensionValue | None = None,
        margin_right: DimensionValue | None = None,
        margin_top: DimensionValue | None = None,
        margin_bottom: DimensionValue | None = None,
        padding_left: LengthPercentageValue | None = None,
        padding_right: LengthPercentageValue | None = None,
        padding_top: LengthPercentageValue | None = None,
        padding_bottom: LengthPercentageValue | None = None,
        border_left: LengthPercentageValue | None = None,
        border_right: LengthPercentageValue | None = None,
        border_top: LengthPercentageValue | None = None,
        border_bottom: LengthPercentageValue | None = None,
        align_items: AlignItems | None = None,
        align_self: AlignItems | None = None,
        justify_items: AlignItems | None = None,
        justify_self: AlignItems | None = None,
        align_content: AlignContent | None = None,
        justify_content: AlignContent | None = None,
        gap_width: LengthPercentageValue | None = None,
        gap_height: LengthPercentageValue | None = None,
        text_align: TextAlign | None = None,
        flex_direction: FlexDirection | None = None,
        flex_wrap: FlexWrap | None = None,
        flex_basis: DimensionValue | None = None,
        flex_grow: float | None = None,
        flex_shrink: float | None = None,
        grid_template_rows: list[GridTrackValue] | None = None,
        grid_template_columns: list[GridTrackValue] | None = None,
        grid_auto_rows: list[GridTrackValue] | None = None,
        grid_auto_columns: list[GridTrackValue] | None = None,
        grid_auto_flow: GridAutoFlow | None = None,
        grid_row: GridPlacement | None = None,
        grid_column: GridPlacement | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __or__(self, other: Style) -> Style: ...
    @property
    def display(self) -> Display: ...
    @property
    def box_sizing(self) -> BoxSizing: ...
    @property
    def overflow_x(self) -> Overflow: ...
    @property
    def overflow_y(self) -> Overflow: ...
    @property
    def scrollbar_width(self) -> float: ...
    @property
    def position(self) -> Position: ...
    @property
    def inset_left(self) -> DimensionValue: ...
    @property
    def inset_right(self) -> DimensionValue: ...
    @property
    def inset_top(self) -> DimensionValue: ...
    @property
    def inset_bottom(self) -> DimensionValue: ...
    @property
    def size_width(self) -> DimensionValue: ...
    @property
    def size_height(self) -> DimensionValue: ...
    @property
    def min_size_width(self) -> DimensionValue: ...
    @property
    def min_size_height(self) -> DimensionValue: ...
    @property
    def max_size_width(self) -> DimensionValue: ...
    @property
    def max_size_height(self) -> DimensionValue: ...
    @property
    def aspect_ratio(self) -> float | None: ...
    @property
    def margin_left(self) -> DimensionValue: ...
    @property
    def margin_right(self) -> DimensionValue: ...
    @property
    def margin_top(self) -> DimensionValue: ...
    @property
    def margin_bottom(self) -> DimensionValue: ...
    @property
    def padding_left(self) -> LengthPercentageValue: ...
    @property
    def padding_right(self) -> LengthPercentageValue: ...
    @property
    def padding_top(self) -> LengthPercentageValue: ...
    @property
    def padding_bottom(self) -> LengthPercentageValue: ...
    @property
    def border_left(self) -> LengthPercentageValue: ...
    @property
    def border_right(self) -> LengthPercentageValue: ...
    @property
    def border_top(self) -> LengthPercentageValue: ...
    @property
    def border_bottom(self) -> LengthPercentageValue: ...
    @property
    def align_items(self) -> AlignItems | None: ...
    @property
    def align_self(self) -> AlignItems | None: ...
    @property
    def justify_items(self) -> AlignItems | None: ...
    @property
    def justify_self(self) -> AlignItems | None: ...
    @property
    def align_content(self) -> AlignContent | None: ...
    @property
    def justify_content(self) -> AlignContent | None: ...
    @property
    def gap_width(self) -> LengthPercentageValue: ...
    @property
    def gap_height(self) -> LengthPercentageValue: ...
    @property
    def text_align(self) -> TextAlign: ...
    @property
    def flex_direction(self) -> FlexDirection: ...
    @property
    def flex_wrap(self) -> FlexWrap: ...
    @property
    def flex_basis(self) -> DimensionValue: ...
    @property
    def flex_grow(self) -> float: ...
    @property
    def flex_shrink(self) -> float: ...
    @property
    def grid_template_rows(self) -> list[GridTrackValue]: ...
    @property
    def grid_template_columns(self) -> list[GridTrackValue]: ...
    @property
    def grid_auto_rows(self) -> list[GridTrackValue]: ...
    @property
    def grid_auto_columns(self) -> list[GridTrackValue]: ...
    @property
    def grid_auto_flow(self) -> GridAutoFlow: ...
    @property
    def grid_row(self) -> GridPlacement: ...
    @property
    def grid_column(self) -> GridPlacement: ...

# Tree

class TaffyTree[NodeContext = object]:
    """A tree of layout nodes."""

    def __init__(self) -> None:
        """Create a new empty layout tree."""
    def __repr__(self) -> str: ...
    @staticmethod
    def with_capacity(capacity: int) -> TaffyTree[NodeContext]:
        """Create a new layout tree with pre-allocated capacity."""
    def new_leaf(self, style: Style) -> NodeId:
        """Create a new leaf node with the given style."""
    def new_leaf_with_context(self, style: Style, context: NodeContext) -> NodeId:
        """Create a new leaf node with the given style and context."""
    def get_node_context(self, node: NodeId) -> NodeContext | None:
        """Get the context attached to a node, if any."""
    def set_node_context(self, node: NodeId, context: NodeContext | None) -> None:
        """Set or clear the context attached to a node."""
    def new_with_children(self, style: Style, children: list[NodeId]) -> NodeId:
        """Create a new node with children."""
    def add_child(self, parent: NodeId, child: NodeId) -> None:
        """Add a child to a parent node."""
    def insert_child_at_index(self, parent: NodeId, child_index: int, child: NodeId) -> None:
        """Insert a child at a specific index."""
    def set_children(self, parent: NodeId, children: list[NodeId]) -> None:
        """Set the children of a node, replacing any existing children."""
    def remove_child(self, parent: NodeId, child: NodeId) -> NodeId:
        """Remove a specific child from a parent."""
    def remove_child_at_index(self, parent: NodeId, child_index: int) -> NodeId:
        """Remove a child at a specific index."""
    def replace_child_at_index(self, parent: NodeId, child_index: int, new_child: NodeId) -> NodeId:
        """Replace the child at a specific index with a new child."""
    def child_at_index(self, parent: NodeId, child_index: int) -> NodeId:
        """Get the child at a specific index."""
    def children(self, parent: NodeId) -> list[NodeId]:
        """Get all children of a node."""
    def child_count(self, parent: NodeId) -> int:
        """Get the number of children of a node."""
    def parent(self, child: NodeId) -> NodeId | None:
        """Get the parent of a node, if any."""
    def total_node_count(self) -> int:
        """Get the total number of nodes in the tree."""
    def remove(self, node: NodeId) -> NodeId:
        """Remove a node from the tree."""
    def clear(self) -> None:
        """Clear all nodes from the tree."""
    def set_style(self, node: NodeId, style: Style) -> None:
        """Set the style of a node."""
    def style(self, node: NodeId) -> Style:
        """Get the style of a node."""
    def mark_dirty(self, node: NodeId) -> None:
        """Mark a node as dirty (needing re-layout)."""
    def dirty(self, node: NodeId) -> bool:
        """Check if a node is dirty (needs re-layout)."""
    def compute_layout(
        self,
        node: NodeId,
        available: AvailableSize | None = None,
        measure: Callable[[KnownSize, AvailableSize, NodeContext], Size] | None = None,
    ) -> None:
        """Compute the layout of a tree rooted at the given node."""
    def layout(self, node: NodeId) -> Layout:
        """Get the computed layout of a node."""
    def unrounded_layout(self, node: NodeId) -> Layout:
        """Get the unrounded layout of a node."""
    def enable_rounding(self) -> None:
        """Enable rounding of layout values."""
    def disable_rounding(self) -> None:
        """Disable rounding of layout values."""
    def print_tree(self, root: NodeId) -> None:
        """Print the layout tree for debugging."""
