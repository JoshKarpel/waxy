import builtins
from collections.abc import Callable, Iterator

# Exceptions

class WaxyException(Exception):
    """Base exception for all waxy errors."""

class TaffyException(WaxyException):
    """Base exception for all taffy errors."""

class InvalidPercent(WaxyException, ValueError):
    """Raised when Percent(value) is called with a value outside [0.0, 1.0]."""

class InvalidLength(WaxyException, ValueError):
    """Raised when Length(value) is called with a NaN value."""

class InvalidGridLine(WaxyException, ValueError):
    """Raised when GridLine(index) is called with index 0 (grid lines are 1-based)."""

class InvalidGridSpan(WaxyException, ValueError):
    """Raised when GridSpan(count) is called with count 0 (must span at least 1 track)."""

class InvalidFlexLineCount(WaxyException, ValueError):
    """Raised when Style(flex_line_count=...) is given 0 (a flex container has at least 1 line)."""

class InvalidRepeat(WaxyException, ValueError):
    """
    Raised when Repeat(...) is given invalid arguments.

    That is: a count of 0, no tracks, or a `line_names` list that is neither empty nor
    one longer than `tracks`.
    """

class InvalidGridTemplateArea(WaxyException, ValueError):
    """Raised when GridTemplateArea(...) has a start line of 0 or an end line before its start."""

class InvalidGridTemplateAreas(WaxyException, ValueError):
    """
    Raised when a GridTemplateAreas is invalid.

    That is: an area extends past `row_count`/`column_count`, two areas share a name, or
    `GridTemplateAreas.from_strings(...)` is given a template CSS would reject (ragged rows,
    non-rectangular areas, or invalid characters).
    """

class InvalidNodeId(TaffyException, KeyError):
    """Raised when a node ID is not valid (node may have been removed)."""

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
    def __hash__(self) -> int: ...
    @property
    def width(self) -> float:
        """The width."""
    @property
    def height(self) -> float:
        """The height."""
    @property
    def area(self) -> float:
        """The area (width * height)."""

class Rect:
    """
    A value for each of the four sides of a box (left, right, top, bottom).

    Mirrors taffy's `Rect<f32>`: per-side values such as `Layout.margin`, `Layout.padding`
    and `Layout.border`, or the edges of a box such as `Layout.scrollable_overflow_rect`.
    """

    def __init__(
        self,
        left: float = 0.0,
        right: float = 0.0,
        top: float = 0.0,
        bottom: float = 0.0,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def left(self) -> float:
        """The value for the left side."""
    @property
    def right(self) -> float:
        """The value for the right side."""
    @property
    def top(self) -> float:
        """The value for the top side."""
    @property
    def bottom(self) -> float:
        """The value for the bottom side."""

class Point:
    """A 2D point with x and y coordinates."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __add__(self, other: Point) -> Point: ...
    def __sub__(self, other: Point) -> Point: ...
    def __mul__(self, scalar: float) -> Point: ...
    def __rmul__(self, scalar: float) -> Point: ...
    def __truediv__(self, scalar: float) -> Point: ...
    def __neg__(self) -> Point: ...
    @property
    def x(self) -> float:
        """The horizontal coordinate."""
    @property
    def y(self) -> float:
        """The vertical coordinate."""

class Line:
    """
    A start and an end value.

    Mirrors taffy's `Line<f32>`, e.g. the start and end positions of a grid track in
    `DetailedGridTracksInfo.positions`.
    """

    def __init__(self, start: float = 0.0, end: float = 0.0) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def start(self) -> float:
        """The start value."""
    @property
    def end(self) -> float:
        """The end value."""

class KnownSize:
    """
    Known dimensions passed to measure functions (independently-optional width/height).

    Passed to the measure callback to indicate which dimensions are already known
    from the node's style. If a dimension is None, the measure function must compute it.

    See: [taffy `Size<Option<f32>>`](https://docs.rs/taffy/0.14.0/taffy/geometry/struct.Size.html)
    """

    def __init__(self, width: float | None = None, height: float | None = None) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __iter__(self) -> Iterator[float | None]: ...
    @property
    def width(self) -> float | None:
        """The known width, or `None` if the measure function must compute it."""
    @property
    def height(self) -> float | None:
        """The known height, or `None` if the measure function must compute it."""

type AvailableSpaceValue = Definite | MinContent | MaxContent
"""Available space value for measure functions: Definite, MinContent, or MaxContent."""

class AvailableSize:
    """
    Available space for measure functions (width/height: Definite | MinContent | MaxContent).

    Passed to the measure callback to indicate how much space is available for layout.
    Each dimension is one of the available-space variants.

    See: [taffy `Size<AvailableSpace>`](https://docs.rs/taffy/0.14.0/taffy/geometry/struct.Size.html)
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
    def width(self) -> AvailableSpaceValue:
        """The space available in the horizontal axis."""
    @property
    def height(self) -> AvailableSpaceValue:
        """The space available in the vertical axis."""

# Value types

class Length:
    """
    A length value in pixels.

    Used for size, padding, border, gap, margin, inset, and grid track sizing fields.

    Raises `InvalidLength` if `value` is NaN.

    See: [taffy `Dimension::Length`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html),
    [MDN `<length>`](https://developer.mozilla.org/en-US/docs/Web/CSS/length)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float:
        """The length in pixels."""

class Percent:
    """
    A percentage value (0.0 to 1.0).

    Used for size, padding, border, gap, margin, inset, and grid track sizing fields.
    Raises InvalidPercent (a subclass of both WaxyException and ValueError) if value
    is outside the range [0.0, 1.0].

    See: [taffy `Dimension::Percent`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html),
    [MDN `<percentage>`](https://developer.mozilla.org/en-US/docs/Web/CSS/percentage)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float:
        """The fraction of the reference size, from 0.0 to 1.0."""

class Auto:
    """
    Automatic sizing or placement.

    Used for size, margin, inset, flex-basis, and grid placement fields.

    See: [taffy `Dimension::Auto`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class MinContent:
    """
    CSS min-content intrinsic sizing.

    The smallest size that can fit the item's contents with all soft line-wrapping
    opportunities taken. Used in `size_*`, `flex_basis`, available space (measure functions),
    and grid track sizing.

    See: [taffy `MinTrackSizingFunction::MinContent`](https://docs.rs/taffy/0.14.0/taffy/style/struct.MinTrackSizingFunction.html),
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
    opportunities taken. Used in `size_*`, `flex_basis`, available space (measure functions),
    and grid track sizing.

    See: [taffy `MinTrackSizingFunction::MaxContent`](https://docs.rs/taffy/0.14.0/taffy/style/struct.MinTrackSizingFunction.html),
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

class Stretch:
    """
    CSS stretch sizing keyword.

    Fills the containing block's available space, less the node's margins.
    Used only in `size_*` and `flex_basis`.

    See: [taffy `Dimension::stretch`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html),
    [MDN `stretch`](https://developer.mozilla.org/en-US/docs/Web/CSS/width#stretch)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class FitContentKeyword:
    """
    CSS fit-content sizing keyword (without a limit).

    Equivalent to `fit-content(stretch)`: the node is sized to its contents, clamped between
    its min-content size and the available space. For an explicit limit, use `FitContent`.
    Used only in `size_*` and `flex_basis`.

    See: [taffy `Dimension::fit_content`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html),
    [MDN `fit-content`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class Content:
    """
    CSS content flex basis keyword.

    Sizes the flex item based on its content, ignoring its `size_*` in the main axis.
    Used only in `flex_basis`.

    See: [taffy `Dimension::content`](https://docs.rs/taffy/0.14.0/taffy/style/struct.Dimension.html),
    [MDN `flex-basis: content`](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis#content)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

STRETCH: Stretch
"""Module-level Stretch singleton. Equivalent to Stretch() but avoids repeated construction."""

FIT_CONTENT: FitContentKeyword
"""Module-level FitContentKeyword singleton. Equivalent to FitContentKeyword() but avoids repeated
construction.
"""

CONTENT: Content
"""Module-level Content singleton. Equivalent to Content() but avoids repeated construction."""

class Definite:
    """
    A definite available space in pixels.

    Used only in AvailableSize (measure function input) to represent a concrete
    pixel measurement of available space.

    See: [taffy `AvailableSpace::Definite`](https://docs.rs/taffy/0.14.0/taffy/style/enum.AvailableSpace.html)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float:
        """The available space in pixels."""

class Fraction:
    """
    A fractional unit of remaining grid space (CSS fr unit).

    After fixed lengths and percentages are allocated, remaining space is divided
    among fractional tracks proportionally. For example, Fraction(1) and Fraction(2)
    in the same grid get 1/3 and 2/3 of remaining space.

    Used only in grid track sizing (grid_template_*, grid_auto_*).

    See: [taffy `MaxTrackSizingFunction::Fraction`](https://docs.rs/taffy/0.14.0/taffy/style/struct.MaxTrackSizingFunction.html),
    [MDN `<flex>` (fr unit)](https://developer.mozilla.org/en-US/docs/Web/CSS/flex_value)
    """

    __match_args__ = ("value",)

    def __init__(self, value: float) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def value(self) -> float:
        """The number of fractional units (the `fr` value)."""

type GridTrackMinValue = Length | Percent | Auto | MinContent | MaxContent
"""Minimum sizing bound for a Minmax grid track."""

type GridTrackMaxValue = Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent
"""Maximum sizing bound for a Minmax grid track."""

type GridTrackValue = (
    Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent
)
"""A grid track sizing value used in grid_template_* and grid_auto_* fields."""

class FitContent:
    """
    CSS fit-content() sizing function.

    Grows up to a specified limit, then clamps: max(min_content, min(max_content, limit)).
    The limit must be a Length or Percent. For the bare `fit-content` keyword, use
    `FIT_CONTENT`.

    Used in `size_*`, `flex_basis`, and grid track sizing.

    See: [taffy `MaxTrackSizingFunction::FitContent`](https://docs.rs/taffy/0.14.0/taffy/style/struct.MaxTrackSizingFunction.html),
    [MDN `fit-content()`](https://developer.mozilla.org/en-US/docs/Web/CSS/fit-content_function)
    """

    __match_args__ = ("limit",)

    def __init__(self, limit: Length | Percent) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def limit(self) -> Length | Percent:
        """The size the node grows to before clamping."""

class Minmax:
    """
    CSS minmax() grid track sizing function.

    Defines a size range: min sets the minimum track size, max sets the maximum.

    - min: Length | Percent | Auto | MinContent | MaxContent
    - max: Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent

    Used only in grid track sizing.

    See: [taffy `TrackSizingFunction`](https://docs.rs/taffy/0.14.0/taffy/style/type.TrackSizingFunction.html),
    [MDN `minmax()`](https://developer.mozilla.org/en-US/docs/Web/CSS/minmax)
    """

    __match_args__ = ("min", "max")

    def __init__(self, min: GridTrackMinValue, max: GridTrackMaxValue) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def min(self) -> GridTrackMinValue:
        """The minimum track size."""
    @property
    def max(self) -> GridTrackMaxValue:
        """The maximum track size."""

class AutoFill:
    """
    CSS auto-fill repetition count.

    Repeat as many times as fit in the container without overflowing, keeping empty tracks.
    Used only as the `count` of a `Repeat`.

    See: [taffy `RepetitionCount::AutoFill`](https://docs.rs/taffy/0.14.0/taffy/style/enum.RepetitionCount.html),
    [MDN `auto-fill`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat#auto-fill)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class AutoFit:
    """
    CSS auto-fit repetition count.

    Like `AutoFill`, but empty repeated tracks collapse to zero size.
    Used only as the `count` of a `Repeat`.

    See: [taffy `RepetitionCount::AutoFit`](https://docs.rs/taffy/0.14.0/taffy/style/enum.RepetitionCount.html),
    [MDN `auto-fit`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat#auto-fit)
    """

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

AUTO_FILL: AutoFill
"""Module-level AutoFill singleton. Equivalent to AutoFill() but avoids repeated construction."""

AUTO_FIT: AutoFit
"""Module-level AutoFit singleton. Equivalent to AutoFit() but avoids repeated construction."""

class Repeat:
    """
    CSS repeat() in `grid_template_rows` / `grid_template_columns`.

    Repeats `tracks` `count` times, where `count` is a positive `int`, `AUTO_FILL`, or
    `AUTO_FIT`. `line_names`, if given, names the lines of each repetition positionally:
    entry `i` names the line before `tracks[i]`, and the final entry names the line after
    the last track, so it has `len(tracks) + 1` entries.

    Raises `InvalidRepeat` if `count` is 0, `tracks` is empty, or `line_names` is neither
    empty nor `len(tracks) + 1` long.

    See: [taffy `GridTemplateRepetition`](https://docs.rs/taffy/0.14.0/taffy/style/struct.GridTemplateRepetition.html),
    [MDN `repeat()`](https://developer.mozilla.org/en-US/docs/Web/CSS/repeat)
    """

    __match_args__ = ("count", "tracks", "line_names")

    def __init__(
        self,
        count: int | AutoFill | AutoFit,
        tracks: list[GridTrackValue],
        line_names: list[list[str]] | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def count(self) -> int | AutoFill | AutoFit:
        """How many times `tracks` repeats."""
    @property
    def tracks(self) -> list[GridTrackValue]:
        """The tracks of one repetition."""
    @property
    def line_names(self) -> list[list[str]]:
        """The names of each line of one repetition (empty if unnamed)."""

type GridTemplateValue = GridTrackValue | Repeat
"""An entry of `grid_template_rows` / `grid_template_columns`: a track or a `Repeat`."""

class GridLine:
    """
    A 1-based grid line index (negative indices count from the end).

    Used in GridPlacement.start and GridPlacement.end.

    Raises `InvalidGridLine` if `index` is 0
    (grid lines are 1-based; negative indices count from the end).

    See: [taffy `GridPlacement::Line`](https://docs.rs/taffy/0.14.0/taffy/style/enum.GridPlacement.html),
    [MDN Line-based placement](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_line-based_placement)
    """

    __match_args__ = ("index",)

    def __init__(self, index: int) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def index(self) -> int:
        """The 1-based line index (negative counts from the end)."""

class GridSpan:
    """
    Span a number of grid tracks.

    Used in GridPlacement.start and GridPlacement.end.

    Raises `InvalidGridSpan` if `count` is 0 (must span at least 1 track).

    See: [taffy `GridPlacement::Span`](https://docs.rs/taffy/0.14.0/taffy/style/enum.GridPlacement.html),
    [MDN `grid-column-start` (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column-start)
    """

    __match_args__ = ("count",)

    def __init__(self, count: int) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def count(self) -> int:
        """The number of tracks spanned."""

class NamedGridLine:
    """
    Place at the `index`th grid line with the given name (counting from the end if negative).

    If no line has that name, the implicit `name-start`/`name-end` lines of a named grid
    area are tried before falling back to the implicit grid, so `NamedGridLine("header")`
    in both `start` and `end` places an item in the `header` area.

    Used in GridPlacement.start and GridPlacement.end.

    Raises `InvalidGridLine` if `index` is 0.

    See: [taffy `GridPlacement::NamedLine`](https://docs.rs/taffy/0.14.0/taffy/style/enum.GridPlacement.html),
    [MDN `grid-row-start`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row-start)
    """

    __match_args__ = ("name", "index")

    def __init__(self, name: str, index: int = 1) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def name(self) -> str:
        """The line name."""
    @property
    def index(self) -> int:
        """Which line with that name, 1-based (negative counts from the end)."""

class NamedGridSpan:
    """
    Span until the `count`th grid line with the given name.

    Used in GridPlacement.start and GridPlacement.end.

    Raises `InvalidGridSpan` if `count` is 0.

    See: [taffy `GridPlacement::NamedSpan`](https://docs.rs/taffy/0.14.0/taffy/style/enum.GridPlacement.html),
    [MDN `grid-row-start` (span)](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row-start)
    """

    __match_args__ = ("name", "count")

    def __init__(self, name: str, count: int = 1) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def name(self) -> str:
        """The line name."""
    @property
    def count(self) -> int:
        """How many lines with that name the item spans across."""

# Enums

class Display:
    """How the node should be displayed."""

    Block: Display
    """Block layout."""
    Flex: Display
    """Flexbox layout."""
    Grid: Display
    """CSS Grid layout."""
    Nil: Display
    """No display (maps to CSS `display: none`)."""
    FlowRoot: Display
    """Block layout that always establishes an independent formatting context."""

class Position:
    """How the node should be positioned."""

    Relative: Position
    """Positioned according to normal flow, then offset."""
    Absolute: Position
    """Removed from normal flow and positioned relative to its containing block."""

class FlexDirection:
    """The direction of a flex container's main axis."""

    Row: FlexDirection
    """Items are laid out in a row (left to right)."""
    Column: FlexDirection
    """Items are laid out in a column (top to bottom)."""
    RowReverse: FlexDirection
    """Items are laid out in a row in reverse order (right to left)."""
    ColumnReverse: FlexDirection
    """Items are laid out in a column in reverse order (bottom to top)."""

class FlexWrap:
    """Whether flex items wrap."""

    NoWrap: FlexWrap
    """Items are forced onto a single line."""
    Wrap: FlexWrap
    """Items wrap onto multiple lines."""
    WrapReverse: FlexWrap
    """Items wrap onto multiple lines in reverse order."""
    Balance: FlexWrap
    """
    Items wrap onto lines of balanced length (CSS `flex-wrap: balance`).

    Lines are balanced into at least `flex_line_count` lines.
    """
    BalanceReverse: FlexWrap
    """Like `Balance`, with lines in reverse order."""

class AlignItems:
    """
    Alignment of items along the cross axis.

    The `Safe*` members are the CSS `safe` variants: an item that would overflow its
    alignment container is aligned as if `Start` instead.
    """

    Start: AlignItems
    """Align to the start of the cross axis."""
    End: AlignItems
    """Align to the end of the cross axis."""
    FlexStart: AlignItems
    """Align to the start of the cross axis (respects `flex-direction`)."""
    FlexEnd: AlignItems
    """Align to the end of the cross axis (respects `flex-direction`)."""
    Center: AlignItems
    """Center along the cross axis."""
    Baseline: AlignItems
    """Align to the first baseline."""
    Stretch: AlignItems
    """Stretch to fill the cross axis."""
    SelfStart: AlignItems
    """Align to the start side of the item's own writing direction."""
    SelfEnd: AlignItems
    """Align to the end side of the item's own writing direction."""
    SafeStart: AlignItems
    """`safe start`."""
    SafeEnd: AlignItems
    """`safe end`."""
    SafeFlexStart: AlignItems
    """`safe flex-start`."""
    SafeFlexEnd: AlignItems
    """`safe flex-end`."""
    SafeCenter: AlignItems
    """`safe center`."""
    SafeSelfStart: AlignItems
    """`safe self-start`."""
    SafeSelfEnd: AlignItems
    """`safe self-end`."""

class AlignContent:
    """
    Alignment of content within the container.

    The `Safe*` members are the CSS `safe` variants: content that would overflow the
    container is aligned as if `Start` instead.
    """

    Start: AlignContent
    """Pack lines to the start of the container."""
    End: AlignContent
    """Pack lines to the end of the container."""
    FlexStart: AlignContent
    """Pack lines to the start of the container (respects `flex-direction`)."""
    FlexEnd: AlignContent
    """Pack lines to the end of the container (respects `flex-direction`)."""
    Center: AlignContent
    """Center lines within the container."""
    Stretch: AlignContent
    """Stretch lines to fill the container."""
    SpaceBetween: AlignContent
    """Distribute lines evenly; first line at start, last at end."""
    SpaceEvenly: AlignContent
    """Distribute lines with equal space around each line."""
    SpaceAround: AlignContent
    """Distribute lines with half-size spaces on the edges."""
    SafeStart: AlignContent
    """`safe start`."""
    SafeEnd: AlignContent
    """`safe end`."""
    SafeFlexStart: AlignContent
    """`safe flex-start`."""
    SafeFlexEnd: AlignContent
    """`safe flex-end`."""
    SafeCenter: AlignContent
    """`safe center`."""

class Overflow:
    """How content overflows its container."""

    Visible: Overflow
    """Content is not clipped and may overflow."""
    Clip: Overflow
    """Content is clipped without a scrollbar."""
    Hidden: Overflow
    """Content is clipped and hidden; scroll position cannot be changed programmatically."""
    Scroll: Overflow
    """Content is clipped but scrollable."""

class GridAutoFlow:
    """How grid items are auto-placed."""

    Row: GridAutoFlow
    """Place items by filling each row."""
    Column: GridAutoFlow
    """Place items by filling each column."""
    RowDense: GridAutoFlow
    """Place items by filling each row, backfilling gaps."""
    ColumnDense: GridAutoFlow
    """Place items by filling each column, backfilling gaps."""

class BoxSizing:
    """Box sizing model."""

    BorderBox: BoxSizing
    """Width and height include padding and border."""
    ContentBox: BoxSizing
    """Width and height apply to the content area only."""

class TextAlign:
    """Text alignment."""

    Auto: TextAlign
    """Automatic text alignment."""
    LegacyLeft: TextAlign
    """Left-aligned text."""
    LegacyRight: TextAlign
    """Right-aligned text."""
    LegacyCenter: TextAlign
    """Centered text."""

class Direction:
    """The inline direction of a node's content (CSS `direction`)."""

    Ltr: Direction
    """Left to right."""
    Rtl: Direction
    """Right to left."""

class Float:
    """Which side a node floats to within a block container (CSS `float`)."""

    Left: Float
    """Float to the left side."""
    Right: Float
    """Float to the right side."""
    Nil: Float
    """Do not float (maps to CSS `float: none`)."""

class Clear:
    """Which preceding floats a node is moved below (CSS `clear`)."""

    Left: Clear
    """Move below left floats."""
    Right: Clear
    """Move below right floats."""
    Both: Clear
    """Move below all floats."""
    Nil: Clear
    """Do not clear floats (maps to CSS `clear: none`)."""

class Contain:
    """CSS containment (`contain`). Taffy supports the `layout` and `paint` containment types."""

    Nil: Contain
    """No containment (maps to CSS `contain: none`)."""
    Layout: Contain
    """
    Layout containment.

    The node establishes an independent formatting context and has no baseline.
    """
    Paint: Contain
    """Paint containment: the node establishes an independent formatting context."""
    Content: Contain
    """Both layout and paint containment (CSS `contain: content`)."""

type GridPlacementValue = GridLine | GridSpan | NamedGridLine | NamedGridSpan | Auto
"""A grid placement value used in GridPlacement start and end."""

class GridPlacement:
    """
    A start/end pair of grid placements for a child item.

    Each of start and end is a GridPlacementValue
    (GridLine | GridSpan | NamedGridLine | NamedGridSpan | Auto).
    Defaults both to Auto (the CSS default for unplaced items).

    See: [taffy `Line<GridPlacement>`](https://docs.rs/taffy/0.14.0/taffy/geometry/struct.Line.html),
    [MDN `grid-row`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row),
    [MDN `grid-column`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)
    """

    def __init__(
        self,
        start: GridPlacementValue | None = None,
        end: GridPlacementValue | None = None,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def start(self) -> GridPlacementValue:
        """The start placement."""
    @property
    def end(self) -> GridPlacementValue:
        """The end placement."""

class GridTemplateArea:
    """
    A named rectangular area of a grid template, bounded by 1-based grid lines.

    An area covering only the first row and first two columns is
    `GridTemplateArea("header", 1, 2, 1, 3)`.

    Raises `InvalidGridTemplateArea` if a start line is 0 or an end line is not after its
    start line.

    See: [taffy `GridTemplateArea`](https://docs.rs/taffy/0.14.0/taffy/style/struct.GridTemplateArea.html),
    [MDN `grid-template-areas`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)
    """

    __match_args__ = ("name", "row_start", "row_end", "column_start", "column_end")

    def __init__(
        self,
        name: str,
        row_start: int,
        row_end: int,
        column_start: int,
        column_end: int,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def name(self) -> str:
        """The area name."""
    @property
    def row_start(self) -> int:
        """The 1-based grid line the area starts at in the row axis."""
    @property
    def row_end(self) -> int:
        """The 1-based grid line the area ends at in the row axis."""
    @property
    def column_start(self) -> int:
        """The 1-based grid line the area starts at in the column axis."""
    @property
    def column_end(self) -> int:
        """The 1-based grid line the area ends at in the column axis."""

class GridTemplateAreas:
    """
    A grid template's named areas, plus its size in tracks (CSS `grid-template-areas`).

    The template can be larger than the extent of its named areas because of unnamed
    cells, so `row_count` and `column_count` are stored explicitly. Most templates are
    easiest to build from CSS strings with `GridTemplateAreas.from_strings`.

    Each area also defines implicit named lines `name-start` and `name-end`, so items can be
    placed into an area with `NamedGridLine(name)`.

    Raises `InvalidGridTemplateAreas` if an area extends past `row_count`/`column_count`,
    or if two areas share a name.

    See: [taffy `GridTemplateAreas`](https://docs.rs/taffy/0.14.0/taffy/style/struct.GridTemplateAreas.html),
    [MDN `grid-template-areas`](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)
    """

    __match_args__ = ("areas", "row_count", "column_count")

    def __init__(
        self,
        areas: list[GridTemplateArea],
        row_count: int,
        column_count: int,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def areas(self) -> list[GridTemplateArea]:
        """The named areas."""
    @property
    def row_count(self) -> int:
        """The number of rows in the template."""
    @property
    def column_count(self) -> int:
        """The number of columns in the template."""
    @staticmethod
    def from_strings(rows: list[str]) -> GridTemplateAreas:
        """
        Parse CSS `grid-template-areas` row strings.

        Each string is one row of whitespace-separated cell names, and `.` marks an unnamed
        cell. For example, `GridTemplateAreas.from_strings(["header header", "nav main"])`.

        Raises `InvalidGridTemplateAreas` if the rows have different numbers of cells, an
        area is not a rectangle, or a row contains a character that is not part of a name.
        """

# Node

class NodeId:
    """A handle to a node in the layout tree."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

# Layout

class Layout:
    """
    The computed layout of a node.

    The layout uses a **border box** coordinate system:

    - [`location`][waxy.Layout.location] is the position of this node's border box origin,
      relative to the **parent's border box** origin (not the parent's content box,
      and not absolute/viewport coordinates). This means a child inside a parent with
      padding or border will have its location offset by the parent's padding + border
      widths. A child's own margin also offsets its location outward from siblings.
    - [`size`][waxy.Layout.size] is the **border box** size: it includes border + padding + content,
      but excludes margin.
    - To compute absolute positions, accumulate [`location`][waxy.Layout.location] values
      from the root down to the node.
    - To compute the content box, subtract [`border`][waxy.Layout.border]
      and [`padding`][waxy.Layout.padding] from [`size`][waxy.Layout.size]
      (or use [`content_box_width()`][waxy.Layout.content_box_width]
      / [`content_box_height()`][waxy.Layout.content_box_height]).
    - To compute the margin box, expand outward from ([`location`][waxy.Layout.location],
      [`size`][waxy.Layout.size]) by the [`margin`][waxy.Layout.margin] widths.

    Note: [`box_sizing`][waxy.Style.box_sizing] does **not** affect the Layout output.
    It only controls how the style's `size_width`/`size_height` inputs are interpreted
    (as border box or content box dimensions). The computed `Layout.size` is always the
    border box. For example, with `padding_left=10, padding_right=10` and `size_width=100`:

    - **`BorderBox`** (default): style size *is* the border box →
      `layout.size.width = 100`, `content_box_width() = 80`
    - **`ContentBox`**: style size is the content box →
      `layout.size.width = 120`, `content_box_width() = 100`
    """

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def order(self) -> int:
        """Topological paint order computed by taffy. Higher values are painted on top."""
    @property
    def location(self) -> Point:
        """Position of this node's border box origin, relative to the parent's border box origin."""
    @property
    def size(self) -> Size:
        """Border box dimensions (includes border + padding + content, excludes margin)."""
    @property
    def scrollable_overflow_rect(self) -> Rect:
        """
        The extent of the node's scrollable overflow, relative to its padding box origin.

        `left`/`top` are `<= 0` (overflow before the scroll origin, which scrolling can't
        reach) and `right`/`bottom` are `>= 0` (the reachable extent of the content).
        """
    @property
    def scrollbar_size(self) -> Size:
        """Size reserved for scrollbars."""
    @property
    def border(self) -> Rect:
        """Resolved border widths on each side."""
    @property
    def padding(self) -> Rect:
        """Resolved padding widths on each side."""
    @property
    def margin(self) -> Rect:
        """Resolved margin widths on each side."""
    def content_box_width(self) -> float:
        """Width of the content box (size minus padding and border)."""
    def content_box_height(self) -> float:
        """Height of the content box (size minus padding and border)."""
    def content_box_size(self) -> Size:
        """Size of the content box (size minus padding and border)."""
    def content_box_x(self) -> float:
        """X offset of the content box, relative to the parent's border box origin."""
    def content_box_y(self) -> float:
        """Y offset of the content box, relative to the parent's border box origin."""
    def scroll_width(self) -> float:
        """The maximum horizontal scroll offset of the node (0 if its content doesn't overflow)."""
    def scroll_height(self) -> float:
        """The maximum vertical scroll offset of the node (0 if its content doesn't overflow)."""

class DetailedGridItemInfo:
    """The placement of one grid item, as 1-based grid line numbers."""

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def row_start(self) -> int:
        """The 1-based grid line the item starts at in the row axis."""
    @property
    def row_end(self) -> int:
        """The 1-based grid line the item ends at in the row axis."""
    @property
    def column_start(self) -> int:
        """The 1-based grid line the item starts at in the column axis."""
    @property
    def column_end(self) -> int:
        """The 1-based grid line the item ends at in the column axis."""

class DetailedGridTracksInfo:
    """
    The computed tracks of one axis (rows or columns) of a grid container.

    Tracks are indexed over the full grid: leading implicit tracks, then explicit tracks,
    then trailing implicit tracks. Line `i` bounds the start of track `i`.
    """

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @property
    def negative_implicit_tracks(self) -> int:
        """Number of implicit tracks before the explicit grid."""
    @property
    def explicit_tracks(self) -> int:
        """Number of explicit tracks."""
    @property
    def positive_implicit_tracks(self) -> int:
        """Number of implicit tracks after the explicit grid."""
    @property
    def positions(self) -> list[Line]:
        """
        The start and end position of each track, relative to the container's border box.

        Positions account for the container's border and padding, gaps, content alignment,
        and collapsed tracks.
        """
    @property
    def line_names(self) -> list[list[str]]:
        """The names of each grid line (one more line than there are tracks)."""
    def names_for_line(self, line_index: int) -> list[str]:
        """The names of the 0-indexed grid line `line_index` (empty if unnamed or out of range)."""

class DetailedGridInfo:
    """
    Detailed results of laying out a grid container: its tracks and item placements.

    Returned by `TaffyTree.detailed_layout_info` for grid containers.
    """

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    @property
    def rows(self) -> DetailedGridTracksInfo:
        """The row tracks."""
    @property
    def columns(self) -> DetailedGridTracksInfo:
        """The column tracks."""
    @property
    def items(self) -> list[DetailedGridItemInfo]:
        """
        The placement of each in-flow grid item.

        Absolutely positioned and `display: Nil` children are not grid items.
        """
    def grid_template_rows(self) -> str:
        """
        The used row sizes and line names, as a CSS `grid-template-rows` resolved value.

        For example, `"[header-start] 20px [header-end] 30px"`.
        """
    def grid_template_columns(self) -> str:
        """The used column sizes and line names, as a CSS `grid-template-columns` resolved value."""
    def item_grid_area(self, item_index: int) -> tuple[Point, Size]:
        """
        The location and size of the grid area occupied by the item at `item_index`.

        `item_index` indexes `items`. The location is relative to the container's border box,
        and the area excludes surrounding gaps. Raises `IndexError` if `item_index` is out of
        range.
        """
    def resolve_absolute_grid_area(
        self,
        grid_row: GridPlacement,
        grid_column: GridPlacement,
        direction: Direction,
        padding_box: Rect,
    ) -> Rect:
        """
        Resolve the grid area for an absolutely positioned box from its grid placement.

        `padding_box` and the returned area are relative to the grid container's border box.
        """

# Style

type DimensionValue = (
    Length | Percent | Auto | MinContent | MaxContent | FitContent | FitContentKeyword | Stretch
)
"""A dimension value used for `size_*`."""

type FlexBasisValue = DimensionValue | Content
"""A flex basis value: any `DimensionValue`, or `Content`."""

type LengthPercentageAutoValue = Length | Percent | Auto
"""A length, percentage, or auto value used for margin, inset, and `min_size_*`/`max_size_*`."""

type LengthPercentageValue = Length | Percent
"""A length-or-percentage value used for padding, border, and gap: Length or Percent."""

class Style:
    """
    Style properties for a layout node.

    All fields are keyword-only. Passing None (or omitting) uses the taffy default.
    Style is immutable — construct a new instance to change fields, or use | to merge.

    A style remembers which fields were explicitly set (see `fields_set`), and `a | b` takes
    each field set in `b` from `b` and every other field from `a`. Two styles are equal only if
    they hold the same values *and* set the same fields, since otherwise they would merge
    differently: `Style() != Style(display=Display.Flex)`, though `Flex` is the default.

    See: [taffy `Style`](https://docs.rs/taffy/0.14.0/taffy/struct.Style.html)
    """

    def __init__(
        self,
        *,
        display: Display | None = None,
        box_sizing: BoxSizing | None = None,
        overflow_x: Overflow | None = None,
        overflow_y: Overflow | None = None,
        scrollbar_width: builtins.float | None = None,
        position: Position | None = None,
        direction: Direction | None = None,
        contain: Contain | None = None,
        float: Float | None = None,
        clear: Clear | None = None,
        item_is_table: bool | None = None,
        item_is_replaced: bool | None = None,
        inset_left: LengthPercentageAutoValue | None = None,
        inset_right: LengthPercentageAutoValue | None = None,
        inset_top: LengthPercentageAutoValue | None = None,
        inset_bottom: LengthPercentageAutoValue | None = None,
        size_width: DimensionValue | None = None,
        size_height: DimensionValue | None = None,
        min_size_width: LengthPercentageAutoValue | None = None,
        min_size_height: LengthPercentageAutoValue | None = None,
        max_size_width: LengthPercentageAutoValue | None = None,
        max_size_height: LengthPercentageAutoValue | None = None,
        aspect_ratio: builtins.float | None = None,
        margin_left: LengthPercentageAutoValue | None = None,
        margin_right: LengthPercentageAutoValue | None = None,
        margin_top: LengthPercentageAutoValue | None = None,
        margin_bottom: LengthPercentageAutoValue | None = None,
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
        flex_basis: FlexBasisValue | None = None,
        flex_grow: builtins.float | None = None,
        flex_shrink: builtins.float | None = None,
        flex_line_count: int | None = None,
        grid_template_rows: list[GridTemplateValue] | None = None,
        grid_template_columns: list[GridTemplateValue] | None = None,
        grid_template_row_names: list[list[str]] | None = None,
        grid_template_column_names: list[list[str]] | None = None,
        grid_template_areas: GridTemplateAreas | None = None,
        grid_auto_rows: list[GridTrackValue] | None = None,
        grid_auto_columns: list[GridTrackValue] | None = None,
        grid_auto_flow: GridAutoFlow | None = None,
        grid_row: GridPlacement | None = None,
        grid_column: GridPlacement | None = None,
    ) -> None:
        """
        Construct a Style with the given fields set.

        All arguments are keyword-only. Omitting or passing None for a field uses
        the taffy default value for that field, except `align_*`/`justify_*` and
        `grid_template_areas`, where None explicitly clears the field. See each property for
        documentation of individual fields.

        Raises `TypeError` for an unknown keyword or a value of the wrong type, and
        `InvalidFlexLineCount` if `flex_line_count` is 0.

        Args:
            display: How the node is laid out (Block, FlowRoot, Flex, Grid, or Nil). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/display)
            box_sizing: Whether size includes border and padding (BorderBox) or not (ContentBox). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)
            overflow_x: How overflowing content is handled horizontally. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-x)
            overflow_y: How overflowing content is handled vertically. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-y)
            scrollbar_width: Width of the scrollbar gutter in pixels. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/scrollbar-gutter)
            position: Whether the node is positioned relative to its parent or absolutely. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/position)
            direction: Inline direction of the node's content (Ltr or Rtl). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/direction)
            contain: Layout and/or paint containment. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/contain)
            float: Which side the node floats to within a block container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/float)
            clear: Which preceding floats the node is moved below. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/clear)
            item_is_table: Whether the node is a table, which block layout sizes differently.
            item_is_replaced: Whether the node is a replaced element (like an image). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Replaced_element)
            inset_left: Left offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/left)
            inset_right: Right offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/right)
            inset_top: Top offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/top)
            inset_bottom: Bottom offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/bottom)
            size_width: Preferred width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/width)
            size_height: Preferred height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/height)
            min_size_width: Minimum width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/min-width)
            min_size_height: Minimum height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/min-height)
            max_size_width: Maximum width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/max-width)
            max_size_height: Maximum height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/max-height)
            aspect_ratio: Preferred aspect ratio (width / height), or None. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio)
            margin_left: Left outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-left)
            margin_right: Right outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-right)
            margin_top: Top outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-top)
            margin_bottom: Bottom outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-bottom)
            padding_left: Left inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-left)
            padding_right: Right inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-right)
            padding_top: Top inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-top)
            padding_bottom: Bottom inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-bottom)
            border_left: Left border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-left-width)
            border_right: Right border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-right-width)
            border_top: Top border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-top-width)
            border_bottom: Bottom border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-bottom-width)
            align_items: Default alignment of children along the cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-items)
            align_self: Override alignment of this node along the parent's cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-self)
            justify_items: Default alignment of children along the main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-items)
            justify_self: Override alignment of this node along the parent's main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-self)
            align_content: Alignment of rows/columns when there is extra space in the cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-content)
            justify_content: Distribution of children along the main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-content)
            gap_width: Horizontal gap between grid/flex items. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/column-gap)
            gap_height: Vertical gap between grid/flex items. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/row-gap)
            text_align: Text alignment within the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/text-align)
            flex_direction: Direction of the flex container's main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-direction)
            flex_wrap: Whether flex items wrap onto multiple lines. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-wrap)
            flex_basis: Default size of a flex item before growing or shrinking. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis)
            flex_grow: Rate at which a flex item grows to fill available space. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-grow)
            flex_shrink: Rate at which a flex item shrinks when space is tight. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-shrink)
            flex_line_count: Minimum number of lines in a multi-line flex container (at least 1). [CSS](https://drafts.csswg.org/css-flexbox-2/#flex-line-count)
            grid_template_rows: Explicit row track sizing in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-rows)
            grid_template_columns: Explicit column track sizing in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-columns)
            grid_template_row_names: Names of the lines between rows. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_named_grid_lines)
            grid_template_column_names: Names of the lines between columns. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_named_grid_lines)
            grid_template_areas: Named areas of the grid template. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)
            grid_auto_rows: Sizing of implicitly-created row tracks. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-rows)
            grid_auto_columns: Sizing of implicitly-created column tracks. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-columns)
            grid_auto_flow: How auto-placed items are inserted in the grid. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-flow)
            grid_row: Row placement of this item in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row)
            grid_column: Column placement of this item in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)
        """
    def __repr__(self) -> str:
        """The explicitly set fields, in declaration order, as constructor syntax."""
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __or__(self, other: Style) -> Style:
        """Merge two styles: fields set in `other` override `self`, others are kept from `self`."""
    @property
    def fields_set(self) -> frozenset[str]:
        """The names of the explicitly set fields."""
    @property
    def display(self) -> Display:
        """How the node is laid out (Block, FlowRoot, Flex, Grid, or Nil). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/display)."""
    @property
    def box_sizing(self) -> BoxSizing:
        """Whether size includes border and padding (BorderBox) or not (ContentBox). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing)."""
    @property
    def overflow_x(self) -> Overflow:
        """How overflowing content is handled horizontally. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-x)."""
    @property
    def overflow_y(self) -> Overflow:
        """How overflowing content is handled vertically. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-y)."""
    @property
    def scrollbar_width(self) -> builtins.float:
        """Width of the scrollbar gutter in pixels. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/scrollbar-gutter)."""
    @property
    def position(self) -> Position:
        """Whether the node is positioned relative to its parent or absolutely. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/position)."""
    @property
    def direction(self) -> Direction:
        """Inline direction of the node's content (Ltr or Rtl). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/direction)."""
    @property
    def contain(self) -> Contain:
        """Layout and/or paint containment. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/contain)."""
    @property
    def float(self) -> Float:
        """Which side the node floats to within a block container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/float)."""
    @property
    def clear(self) -> Clear:
        """Which preceding floats the node is moved below. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/clear)."""
    @property
    def item_is_table(self) -> bool:
        """Whether the node is a table, which block layout sizes differently."""
    @property
    def item_is_replaced(self) -> bool:
        """Whether the node is a replaced element (like an image). [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Replaced_element)."""
    @property
    def inset_left(self) -> LengthPercentageAutoValue:
        """Left offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/left)."""
    @property
    def inset_right(self) -> LengthPercentageAutoValue:
        """Right offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/right)."""
    @property
    def inset_top(self) -> LengthPercentageAutoValue:
        """Top offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/top)."""
    @property
    def inset_bottom(self) -> LengthPercentageAutoValue:
        """Bottom offset for absolutely-positioned nodes. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/bottom)."""
    @property
    def size_width(self) -> DimensionValue:
        """Preferred width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/width)."""
    @property
    def size_height(self) -> DimensionValue:
        """Preferred height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/height)."""
    @property
    def min_size_width(self) -> LengthPercentageAutoValue:
        """Minimum width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/min-width)."""
    @property
    def min_size_height(self) -> LengthPercentageAutoValue:
        """Minimum height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/min-height)."""
    @property
    def max_size_width(self) -> LengthPercentageAutoValue:
        """Maximum width of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/max-width)."""
    @property
    def max_size_height(self) -> LengthPercentageAutoValue:
        """Maximum height of the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/max-height)."""
    @property
    def aspect_ratio(self) -> builtins.float | None:
        """Preferred aspect ratio (width / height), or None. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio)."""
    @property
    def margin_left(self) -> LengthPercentageAutoValue:
        """Left outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-left)."""
    @property
    def margin_right(self) -> LengthPercentageAutoValue:
        """Right outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-right)."""
    @property
    def margin_top(self) -> LengthPercentageAutoValue:
        """Top outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-top)."""
    @property
    def margin_bottom(self) -> LengthPercentageAutoValue:
        """Bottom outer spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/margin-bottom)."""
    @property
    def padding_left(self) -> LengthPercentageValue:
        """Left inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-left)."""
    @property
    def padding_right(self) -> LengthPercentageValue:
        """Right inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-right)."""
    @property
    def padding_top(self) -> LengthPercentageValue:
        """Top inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-top)."""
    @property
    def padding_bottom(self) -> LengthPercentageValue:
        """Bottom inner spacing. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/padding-bottom)."""
    @property
    def border_left(self) -> LengthPercentageValue:
        """Left border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-left-width)."""
    @property
    def border_right(self) -> LengthPercentageValue:
        """Right border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-right-width)."""
    @property
    def border_top(self) -> LengthPercentageValue:
        """Top border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-top-width)."""
    @property
    def border_bottom(self) -> LengthPercentageValue:
        """Bottom border width. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/border-bottom-width)."""
    @property
    def align_items(self) -> AlignItems | None:
        """Default alignment of children along the cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-items)."""
    @property
    def align_self(self) -> AlignItems | None:
        """Override alignment of this node along the parent's cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-self)."""
    @property
    def justify_items(self) -> AlignItems | None:
        """Default alignment of children along the main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-items)."""
    @property
    def justify_self(self) -> AlignItems | None:
        """Override alignment of this node along the parent's main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-self)."""
    @property
    def align_content(self) -> AlignContent | None:
        """Alignment of rows/columns when there is extra space in the cross axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/align-content)."""
    @property
    def justify_content(self) -> AlignContent | None:
        """Distribution of children along the main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/justify-content)."""
    @property
    def gap_width(self) -> LengthPercentageValue:
        """Horizontal gap between grid/flex items. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/column-gap)."""
    @property
    def gap_height(self) -> LengthPercentageValue:
        """Vertical gap between grid/flex items. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/row-gap)."""
    @property
    def text_align(self) -> TextAlign:
        """Text alignment within the node. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/text-align)."""
    @property
    def flex_direction(self) -> FlexDirection:
        """Direction of the flex container's main axis. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-direction)."""
    @property
    def flex_wrap(self) -> FlexWrap:
        """Whether flex items wrap onto multiple lines. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-wrap)."""
    @property
    def flex_basis(self) -> FlexBasisValue:
        """Default size of a flex item before growing or shrinking. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis)."""
    @property
    def flex_grow(self) -> builtins.float:
        """Rate at which a flex item grows to fill available space. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-grow)."""
    @property
    def flex_shrink(self) -> builtins.float:
        """Rate at which a flex item shrinks when space is tight. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-shrink)."""
    @property
    def flex_line_count(self) -> int:
        """Minimum number of lines in a multi-line flex container (at least 1). [CSS](https://drafts.csswg.org/css-flexbox-2/#flex-line-count)."""
    @property
    def grid_template_rows(self) -> list[GridTemplateValue]:
        """Explicit row track sizing in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-rows)."""
    @property
    def grid_template_columns(self) -> list[GridTemplateValue]:
        """Explicit column track sizing in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-columns)."""
    @property
    def grid_template_row_names(self) -> list[list[str]]:
        """
        Names of the lines between rows, positional with `grid_template_rows`.

        Entry `i` names the line before `grid_template_rows[i]` (a `Repeat` counts as one
        entry), and one final entry names the line after the last row.
        [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_named_grid_lines).
        """
    @property
    def grid_template_column_names(self) -> list[list[str]]:
        """
        Names of the lines between columns, positional with `grid_template_columns`.

        Entry `i` names the line before `grid_template_columns[i]` (a `Repeat` counts as one
        entry), and one final entry names the line after the last column.
        [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_using_named_grid_lines).
        """
    @property
    def grid_template_areas(self) -> GridTemplateAreas | None:
        """Named areas of the grid template. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-template-areas)."""
    @property
    def grid_auto_rows(self) -> list[GridTrackValue]:
        """Sizing of implicitly-created row tracks. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-rows)."""
    @property
    def grid_auto_columns(self) -> list[GridTrackValue]:
        """Sizing of implicitly-created column tracks. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-columns)."""
    @property
    def grid_auto_flow(self) -> GridAutoFlow:
        """How auto-placed items are inserted in the grid. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-auto-flow)."""
    @property
    def grid_row(self) -> GridPlacement:
        """Row placement of this item in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row)."""
    @property
    def grid_column(self) -> GridPlacement:
        """Column placement of this item in a grid container. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)."""

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
    def remove_children_range(self, parent: NodeId, start: int, end: int) -> None:
        """
        Detach the children at indices `start` (inclusive) to `end` (exclusive) from a parent.

        The children stay in the tree, without a parent. Raises `ChildIndexOutOfBounds` if
        the range is not within the parent's children.
        """
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
        """
        Set the style of a node.

        Marks the node dirty only if the new style's values differ from the stored style's
        (which fields were explicitly set doesn't matter here), so setting an equal style keeps
        the node's cached layout. Call `mark_dirty` to force a relayout.
        """
    def style(self, node: NodeId) -> Style:
        """
        Get the style of a node.

        taffy doesn't store which fields were explicitly set, so every field of the returned
        style is marked set. It compares equal to the style passed to `set_style` only if that
        style set every field.
        """
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
        """
        Compute the layout of a tree rooted at the given node.

        `measure` is called for leaves with a context to size their content. It must return the
        same size for the same inputs within one call: repeated inputs for the same node are
        answered from the earlier result without calling `measure` again.
        """
    def layout(self, node: NodeId) -> Layout:
        """Get the computed layout of a node."""
    def unrounded_layout(self, node: NodeId) -> Layout:
        """Get the unrounded layout of a node."""
    def absolute_layouts(self, root: NodeId) -> list[tuple[NodeId, Point, Layout]]:
        """
        Every node in the subtree rooted at `root`, in pre-order, with its absolute position.

        The position is relative to the top of the tree (the ancestor with no parent):
        the sum of the node's own and all its ancestors' locations. Each `Layout` is the same as
        `layout(node)` returns, so its `location` stays relative to the node's parent.

        Like `layout`, this follows the tree's rounding setting. With rounding enabled, the
        position is the sum of the unrounded locations, rounded once, which is where taffy's
        rounded `size` assumes the node starts. In taffy 0.14, summing the rounded locations
        instead can be off by a pixel, since it rounds each location relative to its parent
        ([taffy#834](https://github.com/DioxusLabs/taffy/issues/834)).
        """
    def detailed_layout_info(self, node: NodeId) -> DetailedGridInfo | None:
        """
        Get detailed grid layout information for a node.

        Returns None if the node is not a grid container or has not been laid out.
        """
    def enable_rounding(self) -> None:
        """Enable rounding of layout values."""
    def disable_rounding(self) -> None:
        """Disable rounding of layout values."""
    def print_tree(self, root: NodeId) -> None:
        """Print the layout tree to stdout for debugging."""
    def format_tree(self, root: NodeId) -> str:
        """
        An indented dump of the subtree rooted at `root`, one line per node, for debugging.

        Each line gives the node's id, its computed location and size, and the style fields
        that differ from taffy's defaults. Unlike `print_tree`, it returns the string rather
        than writing to stdout.
        """
