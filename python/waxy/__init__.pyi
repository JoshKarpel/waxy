from typing import Optional

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

    width: float
    height: float
    def __init__(self, width: float = 0.0, height: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class Rect:
    """A rectangle with left, right, top, bottom edges."""

    left: float
    right: float
    top: float
    bottom: float
    def __init__(
        self,
        left: float = 0.0,
        right: float = 0.0,
        top: float = 0.0,
        bottom: float = 0.0,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class Point:
    """A 2D point with x and y coordinates."""

    x: float
    y: float
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class Line:
    """A line segment with start and end values."""

    start: float
    end: float
    def __init__(self, start: float = 0.0, end: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

# Dimensions

class Dimension:
    """A dimension value that can be a length, percentage, or auto."""

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
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class LengthPercentage:
    """A length or percentage value (no auto)."""

    @staticmethod
    def length(value: float) -> LengthPercentage:
        """Create a length value in pixels."""
    @staticmethod
    def percent(value: float) -> LengthPercentage:
        """Create a percentage value (0.0 to 1.0)."""
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class LengthPercentageAuto:
    """A length, percentage, or auto value."""

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
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

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
    def __repr__(self) -> str: ...

# Grid types

class GridTrack:
    """A track sizing function for grid layouts (minmax(min, max))."""

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
    def __repr__(self) -> str: ...

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

    @staticmethod
    def auto() -> GridPlacement:
        """Auto placement."""
    @staticmethod
    def line(index: int) -> GridPlacement:
        """Place at a specific line index (1-based, negative counts from end)."""
    @staticmethod
    def span(count: int) -> GridPlacement:
        """Span a number of tracks."""
    def __repr__(self) -> str: ...

class GridLine:
    """A line with start and end grid placements."""

    start: GridPlacement
    end: GridPlacement
    def __init__(
        self,
        start: Optional[GridPlacement] = None,
        end: Optional[GridPlacement] = None,
    ) -> None: ...
    def __repr__(self) -> str: ...

# Node

class NodeId:
    """A handle to a node in the layout tree."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

# Layout

class Layout:
    """The computed layout of a node."""

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
    def __repr__(self) -> str: ...

# Style

class Style:
    """Style properties for a layout node."""

    def __init__(
        self,
        *,
        display: Optional[Display] = None,
        box_sizing: Optional[BoxSizing] = None,
        overflow_x: Optional[Overflow] = None,
        overflow_y: Optional[Overflow] = None,
        scrollbar_width: Optional[float] = None,
        position: Optional[Position] = None,
        inset_left: Optional[LengthPercentageAuto] = None,
        inset_right: Optional[LengthPercentageAuto] = None,
        inset_top: Optional[LengthPercentageAuto] = None,
        inset_bottom: Optional[LengthPercentageAuto] = None,
        size_width: Optional[Dimension] = None,
        size_height: Optional[Dimension] = None,
        min_size_width: Optional[Dimension] = None,
        min_size_height: Optional[Dimension] = None,
        max_size_width: Optional[Dimension] = None,
        max_size_height: Optional[Dimension] = None,
        aspect_ratio: Optional[float] = None,
        margin_left: Optional[LengthPercentageAuto] = None,
        margin_right: Optional[LengthPercentageAuto] = None,
        margin_top: Optional[LengthPercentageAuto] = None,
        margin_bottom: Optional[LengthPercentageAuto] = None,
        padding_left: Optional[LengthPercentage] = None,
        padding_right: Optional[LengthPercentage] = None,
        padding_top: Optional[LengthPercentage] = None,
        padding_bottom: Optional[LengthPercentage] = None,
        border_left: Optional[LengthPercentage] = None,
        border_right: Optional[LengthPercentage] = None,
        border_top: Optional[LengthPercentage] = None,
        border_bottom: Optional[LengthPercentage] = None,
        align_items: Optional[AlignItems] = None,
        align_self: Optional[AlignItems] = None,
        justify_items: Optional[AlignItems] = None,
        justify_self: Optional[AlignItems] = None,
        align_content: Optional[AlignContent] = None,
        justify_content: Optional[AlignContent] = None,
        gap_width: Optional[LengthPercentage] = None,
        gap_height: Optional[LengthPercentage] = None,
        text_align: Optional[TextAlign] = None,
        flex_direction: Optional[FlexDirection] = None,
        flex_wrap: Optional[FlexWrap] = None,
        flex_basis: Optional[Dimension] = None,
        flex_grow: Optional[float] = None,
        flex_shrink: Optional[float] = None,
        grid_template_rows: Optional[list[GridTrack]] = None,
        grid_template_columns: Optional[list[GridTrack]] = None,
        grid_auto_rows: Optional[list[GridTrack]] = None,
        grid_auto_columns: Optional[list[GridTrack]] = None,
        grid_auto_flow: Optional[GridAutoFlow] = None,
        grid_row: Optional[GridLine] = None,
        grid_column: Optional[GridLine] = None,
    ) -> None: ...

    # Properties
    display: Display
    box_sizing: BoxSizing
    overflow_x: Overflow
    overflow_y: Overflow
    scrollbar_width: float
    position: Position
    inset_left: LengthPercentageAuto
    inset_right: LengthPercentageAuto
    inset_top: LengthPercentageAuto
    inset_bottom: LengthPercentageAuto
    size_width: Dimension
    size_height: Dimension
    min_size_width: Dimension
    min_size_height: Dimension
    max_size_width: Dimension
    max_size_height: Dimension
    aspect_ratio: Optional[float]
    margin_left: LengthPercentageAuto
    margin_right: LengthPercentageAuto
    margin_top: LengthPercentageAuto
    margin_bottom: LengthPercentageAuto
    padding_left: LengthPercentage
    padding_right: LengthPercentage
    padding_top: LengthPercentage
    padding_bottom: LengthPercentage
    border_left: LengthPercentage
    border_right: LengthPercentage
    border_top: LengthPercentage
    border_bottom: LengthPercentage
    align_items: Optional[AlignItems]
    align_self: Optional[AlignItems]
    justify_items: Optional[AlignItems]
    justify_self: Optional[AlignItems]
    align_content: Optional[AlignContent]
    justify_content: Optional[AlignContent]
    gap_width: LengthPercentage
    gap_height: LengthPercentage
    text_align: TextAlign
    flex_direction: FlexDirection
    flex_wrap: FlexWrap
    flex_basis: Dimension
    flex_grow: float
    flex_shrink: float
    grid_template_rows: list[GridTrack]
    grid_template_columns: list[GridTrack]
    grid_auto_rows: list[GridTrack]
    grid_auto_columns: list[GridTrack]
    grid_auto_flow: GridAutoFlow
    grid_row: GridLine
    grid_column: GridLine

    def __repr__(self) -> str: ...

# Tree

class TaffyTree:
    """A tree of layout nodes."""

    def __init__(self) -> None:
        """Create a new empty layout tree."""
    @staticmethod
    def with_capacity(capacity: int) -> TaffyTree:
        """Create a new layout tree with pre-allocated capacity."""
    def new_leaf(self, style: Style) -> NodeId:
        """Create a new leaf node with the given style."""
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
    def parent(self, child: NodeId) -> Optional[NodeId]:
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
        available_width: Optional[AvailableSpace] = None,
        available_height: Optional[AvailableSpace] = None,
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
    def __repr__(self) -> str: ...

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
