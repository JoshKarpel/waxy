from collections.abc import Callable, Iterator

# Exceptions

class TaffyException(Exception):
    """Base exception for all taffy errors."""

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

class KnownDimensions:
    """Known dimensions passed to measure functions (independently-optional width/height)."""

    def __init__(self, width: float | None = None, height: float | None = None) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[float | None]: ...
    @property
    def width(self) -> float | None: ...
    @property
    def height(self) -> float | None: ...

class AvailableDimensions:
    """Available dimensions passed to measure functions (width/height as AvailableSpace)."""

    def __init__(self, width: AvailableSpace, height: AvailableSpace) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[AvailableSpace]: ...
    @property
    def width(self) -> AvailableSpace: ...
    @property
    def height(self) -> AvailableSpace: ...

# Dimensions

class Dimension:
    """A dimension value that can be a length, percentage, or auto."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @staticmethod
    def length(value: float) -> Dimension:
        """Create a length dimension in pixels."""
    @staticmethod
    def percent(value: float) -> Dimension:
        """Create a percentage dimension (0.0 to 1.0)."""
    @staticmethod
    def auto() -> Dimension:
        """Create an auto dimension."""
    def is_auto(self) -> bool: ...

class LengthPercentage:
    """A length or percentage value (no auto)."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @staticmethod
    def length(value: float) -> LengthPercentage:
        """Create a length value in pixels."""
    @staticmethod
    def percent(value: float) -> LengthPercentage:
        """Create a percentage value (0.0 to 1.0)."""

class LengthPercentageAuto:
    """A length, percentage, or auto value."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @staticmethod
    def length(value: float) -> LengthPercentageAuto:
        """Create a length value in pixels."""
    @staticmethod
    def percent(value: float) -> LengthPercentageAuto:
        """Create a percentage value (0.0 to 1.0)."""
    @staticmethod
    def auto() -> LengthPercentageAuto:
        """Create an auto value."""
    def is_auto(self) -> bool: ...

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

class AvailableSpace:
    """Available space for layout."""

    def __repr__(self) -> str: ...
    @staticmethod
    def definite(value: float) -> AvailableSpace:
        """Create a definite available space."""
    @staticmethod
    def min_content() -> AvailableSpace:
        """Create a min-content available space."""
    @staticmethod
    def max_content() -> AvailableSpace:
        """Create a max-content available space."""
    def is_definite(self) -> bool: ...
    def is_min_content(self) -> bool: ...
    def is_max_content(self) -> bool: ...
    def value(self) -> float | None:
        """Return the definite value, or None for min-content/max-content."""

# Grid types

class GridTrack:
    """A track sizing function for grid layouts (minmax(min, max))."""

    def __repr__(self) -> str: ...
    @staticmethod
    def length(value: float) -> GridTrack:
        """Create a fixed-size track from a length in pixels."""
    @staticmethod
    def percent(value: float) -> GridTrack:
        """Create a fixed-size track from a percentage."""
    @staticmethod
    def flex(value: float) -> GridTrack:
        """Create a flexible track (fr unit)."""
    @staticmethod
    def auto() -> GridTrack:
        """Create an auto-sized track."""
    @staticmethod
    def min_content() -> GridTrack:
        """Create a min-content track."""
    @staticmethod
    def max_content() -> GridTrack:
        """Create a max-content track."""
    @staticmethod
    def minmax(min_value: GridTrackMin, max_value: GridTrackMax) -> GridTrack:
        """Create a minmax track with separate min and max sizing functions."""
    @staticmethod
    def fit_content_px(limit: float) -> GridTrack:
        """Create a fit-content track with a pixel limit."""
    @staticmethod
    def fit_content_percent(limit: float) -> GridTrack:
        """Create a fit-content track with a percentage limit."""

class GridTrackMin:
    """Min track sizing function (for use with GridTrack.minmax)."""

    @staticmethod
    def length(value: float) -> GridTrackMin:
        """Create a fixed min size from a length in pixels."""
    @staticmethod
    def percent(value: float) -> GridTrackMin:
        """Create a fixed min size from a percentage."""
    @staticmethod
    def auto() -> GridTrackMin:
        """Create an auto min size."""
    @staticmethod
    def min_content() -> GridTrackMin:
        """Create a min-content min size."""
    @staticmethod
    def max_content() -> GridTrackMin:
        """Create a max-content min size."""

class GridTrackMax:
    """Max track sizing function (for use with GridTrack.minmax)."""

    @staticmethod
    def length(value: float) -> GridTrackMax:
        """Create a fixed max size from a length in pixels."""
    @staticmethod
    def percent(value: float) -> GridTrackMax:
        """Create a fixed max size from a percentage."""
    @staticmethod
    def auto() -> GridTrackMax:
        """Create an auto max size."""
    @staticmethod
    def min_content() -> GridTrackMax:
        """Create a min-content max size."""
    @staticmethod
    def max_content() -> GridTrackMax:
        """Create a max-content max size."""
    @staticmethod
    def fr(value: float) -> GridTrackMax:
        """Create a fractional max size (fr unit)."""
    @staticmethod
    def fit_content_px(limit: float) -> GridTrackMax:
        """Create a fit-content max size with a pixel limit."""
    @staticmethod
    def fit_content_percent(limit: float) -> GridTrackMax:
        """Create a fit-content max size with a percentage limit."""

class GridPlacement:
    """Grid placement for a child item."""

    def __repr__(self) -> str: ...
    @staticmethod
    def auto() -> GridPlacement:
        """Auto placement."""
    @staticmethod
    def line(index: int) -> GridPlacement:
        """Place at a specific line index (1-based, negative counts from end)."""
    @staticmethod
    def span(count: int) -> GridPlacement:
        """Span a number of tracks."""

class GridLine:
    """A line with start and end grid placements."""

    def __init__(
        self,
        start: GridPlacement | None = None,
        end: GridPlacement | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def start(self) -> GridPlacement: ...
    @property
    def end(self) -> GridPlacement: ...

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

class Style:
    """Style properties for a layout node."""

    def __init__(
        self,
        *,
        display: Display | None = None,
        box_sizing: BoxSizing | None = None,
        overflow_x: Overflow | None = None,
        overflow_y: Overflow | None = None,
        scrollbar_width: float | None = None,
        position: Position | None = None,
        inset_left: LengthPercentageAuto | None = None,
        inset_right: LengthPercentageAuto | None = None,
        inset_top: LengthPercentageAuto | None = None,
        inset_bottom: LengthPercentageAuto | None = None,
        size_width: Dimension | None = None,
        size_height: Dimension | None = None,
        min_size_width: Dimension | None = None,
        min_size_height: Dimension | None = None,
        max_size_width: Dimension | None = None,
        max_size_height: Dimension | None = None,
        aspect_ratio: float | None = None,
        margin_left: LengthPercentageAuto | None = None,
        margin_right: LengthPercentageAuto | None = None,
        margin_top: LengthPercentageAuto | None = None,
        margin_bottom: LengthPercentageAuto | None = None,
        padding_left: LengthPercentage | None = None,
        padding_right: LengthPercentage | None = None,
        padding_top: LengthPercentage | None = None,
        padding_bottom: LengthPercentage | None = None,
        border_left: LengthPercentage | None = None,
        border_right: LengthPercentage | None = None,
        border_top: LengthPercentage | None = None,
        border_bottom: LengthPercentage | None = None,
        align_items: AlignItems | None = None,
        align_self: AlignItems | None = None,
        justify_items: AlignItems | None = None,
        justify_self: AlignItems | None = None,
        align_content: AlignContent | None = None,
        justify_content: AlignContent | None = None,
        gap_width: LengthPercentage | None = None,
        gap_height: LengthPercentage | None = None,
        text_align: TextAlign | None = None,
        flex_direction: FlexDirection | None = None,
        flex_wrap: FlexWrap | None = None,
        flex_basis: Dimension | None = None,
        flex_grow: float | None = None,
        flex_shrink: float | None = None,
        grid_template_rows: list[GridTrack] | None = None,
        grid_template_columns: list[GridTrack] | None = None,
        grid_auto_rows: list[GridTrack] | None = None,
        grid_auto_columns: list[GridTrack] | None = None,
        grid_auto_flow: GridAutoFlow | None = None,
        grid_row: GridLine | None = None,
        grid_column: GridLine | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __or__(self, other: Style) -> Style: ...
    # Properties (read-only)
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
    def inset_left(self) -> LengthPercentageAuto: ...
    @property
    def inset_right(self) -> LengthPercentageAuto: ...
    @property
    def inset_top(self) -> LengthPercentageAuto: ...
    @property
    def inset_bottom(self) -> LengthPercentageAuto: ...
    @property
    def size_width(self) -> Dimension: ...
    @property
    def size_height(self) -> Dimension: ...
    @property
    def min_size_width(self) -> Dimension: ...
    @property
    def min_size_height(self) -> Dimension: ...
    @property
    def max_size_width(self) -> Dimension: ...
    @property
    def max_size_height(self) -> Dimension: ...
    @property
    def aspect_ratio(self) -> float | None: ...
    @property
    def margin_left(self) -> LengthPercentageAuto: ...
    @property
    def margin_right(self) -> LengthPercentageAuto: ...
    @property
    def margin_top(self) -> LengthPercentageAuto: ...
    @property
    def margin_bottom(self) -> LengthPercentageAuto: ...
    @property
    def padding_left(self) -> LengthPercentage: ...
    @property
    def padding_right(self) -> LengthPercentage: ...
    @property
    def padding_top(self) -> LengthPercentage: ...
    @property
    def padding_bottom(self) -> LengthPercentage: ...
    @property
    def border_left(self) -> LengthPercentage: ...
    @property
    def border_right(self) -> LengthPercentage: ...
    @property
    def border_top(self) -> LengthPercentage: ...
    @property
    def border_bottom(self) -> LengthPercentage: ...
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
    def gap_width(self) -> LengthPercentage: ...
    @property
    def gap_height(self) -> LengthPercentage: ...
    @property
    def text_align(self) -> TextAlign: ...
    @property
    def flex_direction(self) -> FlexDirection: ...
    @property
    def flex_wrap(self) -> FlexWrap: ...
    @property
    def flex_basis(self) -> Dimension: ...
    @property
    def flex_grow(self) -> float: ...
    @property
    def flex_shrink(self) -> float: ...
    @property
    def grid_template_rows(self) -> list[GridTrack]: ...
    @property
    def grid_template_columns(self) -> list[GridTrack]: ...
    @property
    def grid_auto_rows(self) -> list[GridTrack]: ...
    @property
    def grid_auto_columns(self) -> list[GridTrack]: ...
    @property
    def grid_auto_flow(self) -> GridAutoFlow: ...
    @property
    def grid_row(self) -> GridLine: ...
    @property
    def grid_column(self) -> GridLine: ...

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
        available_space: AvailableDimensions | None = None,
        measure: Callable[[KnownDimensions, AvailableDimensions, NodeContext], Size] | None = None,
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

# Helper functions

def zero() -> LengthPercentage:
    """Create a zero-length value."""

def auto() -> Dimension:
    """Create an auto dimension."""

def length(value: float) -> Dimension:
    """Create a length dimension in pixels."""

def percent(value: float) -> Dimension:
    """Create a percentage dimension."""

def min_content() -> AvailableSpace:
    """Create a min-content available space."""

def max_content() -> AvailableSpace:
    """Create a max-content available space."""

def fr(value: float) -> GridTrack:
    """Create a flexible grid track (fr unit)."""

def minmax(min: GridTrackMin, max: GridTrackMax) -> GridTrack:
    """Create a minmax grid track."""
