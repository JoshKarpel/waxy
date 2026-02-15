from typing import Optional

# Exceptions
class TaffyException(Exception): ...
class ChildIndexOutOfBounds(TaffyException): ...
class InvalidParentNode(TaffyException): ...
class InvalidChildNode(TaffyException): ...
class InvalidInputNode(TaffyException): ...

# Geometry
class Size:
    width: float
    height: float
    def __init__(self, width: float = 0.0, height: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class Rect:
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
    x: float
    y: float
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class Line:
    start: float
    end: float
    def __init__(self, start: float = 0.0, end: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

# Dimensions
class Dimension:
    @staticmethod
    def length(value: float) -> Dimension: ...
    @staticmethod
    def percent(value: float) -> Dimension: ...
    @staticmethod
    def auto() -> Dimension: ...
    def is_auto(self) -> bool: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class LengthPercentage:
    @staticmethod
    def length(value: float) -> LengthPercentage: ...
    @staticmethod
    def percent(value: float) -> LengthPercentage: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

class LengthPercentageAuto:
    @staticmethod
    def length(value: float) -> LengthPercentageAuto: ...
    @staticmethod
    def percent(value: float) -> LengthPercentageAuto: ...
    @staticmethod
    def auto() -> LengthPercentageAuto: ...
    def is_auto(self) -> bool: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...

# Enums
class Display:
    Block: Display
    Flex: Display
    Grid: Display
    Nil: Display

class Position:
    Relative: Position
    Absolute: Position

class FlexDirection:
    Row: FlexDirection
    Column: FlexDirection
    RowReverse: FlexDirection
    ColumnReverse: FlexDirection

class FlexWrap:
    NoWrap: FlexWrap
    Wrap: FlexWrap
    WrapReverse: FlexWrap

class AlignItems:
    Start: AlignItems
    End: AlignItems
    FlexStart: AlignItems
    FlexEnd: AlignItems
    Center: AlignItems
    Baseline: AlignItems
    Stretch: AlignItems

class AlignContent:
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
    Visible: Overflow
    Clip: Overflow
    Hidden: Overflow
    Scroll: Overflow

class GridAutoFlow:
    Row: GridAutoFlow
    Column: GridAutoFlow
    RowDense: GridAutoFlow
    ColumnDense: GridAutoFlow

class BoxSizing:
    BorderBox: BoxSizing
    ContentBox: BoxSizing

class TextAlign:
    Auto: TextAlign
    LegacyLeft: TextAlign
    LegacyRight: TextAlign
    LegacyCenter: TextAlign

class AvailableSpace:
    @staticmethod
    def definite(value: float) -> AvailableSpace: ...
    @staticmethod
    def min_content() -> AvailableSpace: ...
    @staticmethod
    def max_content() -> AvailableSpace: ...
    def is_definite(self) -> bool: ...
    def __repr__(self) -> str: ...

# Grid types
class GridTrack:
    @staticmethod
    def length(value: float) -> GridTrack: ...
    @staticmethod
    def percent(value: float) -> GridTrack: ...
    @staticmethod
    def flex(value: float) -> GridTrack: ...
    @staticmethod
    def auto() -> GridTrack: ...
    @staticmethod
    def min_content() -> GridTrack: ...
    @staticmethod
    def max_content() -> GridTrack: ...
    @staticmethod
    def minmax(min_value: GridTrackMin, max_value: GridTrackMax) -> GridTrack: ...
    @staticmethod
    def fit_content_px(limit: float) -> GridTrack: ...
    @staticmethod
    def fit_content_percent(limit: float) -> GridTrack: ...
    def __repr__(self) -> str: ...

class GridTrackMin:
    @staticmethod
    def length(value: float) -> GridTrackMin: ...
    @staticmethod
    def percent(value: float) -> GridTrackMin: ...
    @staticmethod
    def auto() -> GridTrackMin: ...
    @staticmethod
    def min_content() -> GridTrackMin: ...
    @staticmethod
    def max_content() -> GridTrackMin: ...

class GridTrackMax:
    @staticmethod
    def length(value: float) -> GridTrackMax: ...
    @staticmethod
    def percent(value: float) -> GridTrackMax: ...
    @staticmethod
    def auto() -> GridTrackMax: ...
    @staticmethod
    def min_content() -> GridTrackMax: ...
    @staticmethod
    def max_content() -> GridTrackMax: ...
    @staticmethod
    def fr(value: float) -> GridTrackMax: ...
    @staticmethod
    def fit_content_px(limit: float) -> GridTrackMax: ...
    @staticmethod
    def fit_content_percent(limit: float) -> GridTrackMax: ...

class GridPlacement:
    @staticmethod
    def auto() -> GridPlacement: ...
    @staticmethod
    def line(index: int) -> GridPlacement: ...
    @staticmethod
    def span(count: int) -> GridPlacement: ...
    def __repr__(self) -> str: ...

class GridLine:
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
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

# Layout
class Layout:
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
    def content_box_width(self) -> float: ...
    def content_box_height(self) -> float: ...
    def __repr__(self) -> str: ...

# Style
class Style:
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
    def __init__(self) -> None: ...
    @staticmethod
    def with_capacity(capacity: int) -> TaffyTree: ...
    def new_leaf(self, style: Style) -> NodeId: ...
    def new_with_children(self, style: Style, children: list[NodeId]) -> NodeId: ...
    def add_child(self, parent: NodeId, child: NodeId) -> None: ...
    def insert_child_at_index(self, parent: NodeId, child_index: int, child: NodeId) -> None: ...
    def set_children(self, parent: NodeId, children: list[NodeId]) -> None: ...
    def remove_child(self, parent: NodeId, child: NodeId) -> NodeId: ...
    def remove_child_at_index(self, parent: NodeId, child_index: int) -> NodeId: ...
    def replace_child_at_index(
        self, parent: NodeId, child_index: int, new_child: NodeId
    ) -> NodeId: ...
    def child_at_index(self, parent: NodeId, child_index: int) -> NodeId: ...
    def children(self, parent: NodeId) -> list[NodeId]: ...
    def child_count(self, parent: NodeId) -> int: ...
    def parent(self, child: NodeId) -> Optional[NodeId]: ...
    def total_node_count(self) -> int: ...
    def remove(self, node: NodeId) -> NodeId: ...
    def clear(self) -> None: ...
    def set_style(self, node: NodeId, style: Style) -> None: ...
    def style(self, node: NodeId) -> Style: ...
    def mark_dirty(self, node: NodeId) -> None: ...
    def dirty(self, node: NodeId) -> bool: ...
    def compute_layout(
        self,
        node: NodeId,
        available_width: Optional[AvailableSpace] = None,
        available_height: Optional[AvailableSpace] = None,
    ) -> None: ...
    def layout(self, node: NodeId) -> Layout: ...
    def unrounded_layout(self, node: NodeId) -> Layout: ...
    def enable_rounding(self) -> None: ...
    def disable_rounding(self) -> None: ...
    def print_tree(self, root: NodeId) -> None: ...
    def __repr__(self) -> str: ...

# Helper functions
def zero() -> LengthPercentage: ...
def auto() -> Dimension: ...
def length(value: float) -> Dimension: ...
def percent(value: float) -> Dimension: ...
def min_content() -> AvailableSpace: ...
def max_content() -> AvailableSpace: ...
def fr(value: float) -> GridTrack: ...
def minmax(min: GridTrackMin, max: GridTrackMax) -> GridTrack: ...
