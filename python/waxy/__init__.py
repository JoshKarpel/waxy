"""Waxy: A Python wrapper around the Rust taffy UI layout library."""

from waxy._waxy import (
    AUTO,
    AUTO_FILL,
    AUTO_FIT,
    CONTENT,
    FIT_CONTENT,
    MAX_CONTENT,
    MIN_CONTENT,
    STRETCH,
    AlignContent,
    AlignItems,
    Auto,
    AutoFill,
    AutoFit,
    AvailableSize,
    BoxSizing,
    ChildIndexOutOfBounds,
    Clear,
    Contain,
    Content,
    Definite,
    DetailedGridInfo,
    DetailedGridItemInfo,
    DetailedGridTracksInfo,
    Direction,
    Display,
    FitContent,
    FitContentKeyword,
    FlexDirection,
    FlexWrap,
    Float,
    Fraction,
    GridAutoFlow,
    GridLine,
    GridPlacement,
    GridSpan,
    GridTemplateArea,
    GridTemplateAreas,
    InvalidChildNode,
    InvalidFlexLineCount,
    InvalidGridLine,
    InvalidGridSpan,
    InvalidGridTemplateArea,
    InvalidGridTemplateAreas,
    InvalidInputNode,
    InvalidLength,
    InvalidNodeId,
    InvalidParentNode,
    InvalidPercent,
    InvalidRepeat,
    KnownSize,
    Layout,
    Length,
    Line,
    MaxContent,
    MinContent,
    Minmax,
    NamedGridLine,
    NamedGridSpan,
    NodeId,
    Overflow,
    Percent,
    Point,
    Position,
    Rect,
    Repeat,
    Size,
    Stretch,
    Style,
    TaffyException,
    TaffyTree,
    TextAlign,
    WaxyException,
)

type AvailableSpaceValue = Definite | MinContent | MaxContent
"""Available space value for measure functions: Definite, MinContent, or MaxContent."""

type DimensionValue = (
    Length | Percent | Auto | MinContent | MaxContent | FitContent | FitContentKeyword | Stretch
)
"""A dimension value used for `size_*`."""

type FlexBasisValue = DimensionValue | Content
"""A flex basis value: any `DimensionValue`, or `Content`."""

type GridPlacementValue = GridLine | GridSpan | NamedGridLine | NamedGridSpan | Auto
"""A grid placement value used in GridPlacement start and end."""

type GridTrackMaxValue = Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent
"""Maximum sizing bound for a Minmax grid track."""

type GridTrackMinValue = Length | Percent | Auto | MinContent | MaxContent
"""Minimum sizing bound for a Minmax grid track."""

type GridTrackValue = (
    Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent
)
"""A grid track sizing value used in grid_template_* and grid_auto_* fields."""

type GridTemplateValue = GridTrackValue | Repeat
"""An entry of `grid_template_rows` / `grid_template_columns`: a track or a `Repeat`."""

type LengthPercentageAutoValue = Length | Percent | Auto
"""A length, percentage, or auto value used for margin, inset, and `min_size_*`/`max_size_*`."""

type LengthPercentageValue = Length | Percent
"""A length-or-percentage value used for padding, border, and gap: Length or Percent."""

__all__ = [
    "AUTO",
    "AUTO_FILL",
    "AUTO_FIT",
    "CONTENT",
    "FIT_CONTENT",
    "MAX_CONTENT",
    "MIN_CONTENT",
    "STRETCH",
    "AlignContent",
    "AlignItems",
    "Auto",
    "AutoFill",
    "AutoFit",
    "AvailableSize",
    "AvailableSpaceValue",
    "BoxSizing",
    "ChildIndexOutOfBounds",
    "Clear",
    "Contain",
    "Content",
    "Definite",
    "DetailedGridInfo",
    "DetailedGridItemInfo",
    "DetailedGridTracksInfo",
    "DimensionValue",
    "Direction",
    "Display",
    "FitContent",
    "FitContentKeyword",
    "FlexBasisValue",
    "FlexDirection",
    "FlexWrap",
    "Float",
    "Fraction",
    "GridAutoFlow",
    "GridLine",
    "GridPlacement",
    "GridPlacementValue",
    "GridSpan",
    "GridTemplateArea",
    "GridTemplateAreas",
    "GridTemplateValue",
    "GridTrackMaxValue",
    "GridTrackMinValue",
    "GridTrackValue",
    "InvalidChildNode",
    "InvalidFlexLineCount",
    "InvalidGridLine",
    "InvalidGridSpan",
    "InvalidGridTemplateArea",
    "InvalidGridTemplateAreas",
    "InvalidInputNode",
    "InvalidLength",
    "InvalidNodeId",
    "InvalidParentNode",
    "InvalidPercent",
    "InvalidRepeat",
    "KnownSize",
    "Layout",
    "Length",
    "LengthPercentageAutoValue",
    "LengthPercentageValue",
    "Line",
    "MaxContent",
    "MinContent",
    "Minmax",
    "NamedGridLine",
    "NamedGridSpan",
    "NodeId",
    "Overflow",
    "Percent",
    "Point",
    "Position",
    "Rect",
    "Repeat",
    "Size",
    "Stretch",
    "Style",
    "TaffyException",
    "TaffyTree",
    "TextAlign",
    "WaxyException",
]
