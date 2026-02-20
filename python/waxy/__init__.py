"""Waxy: A Python wrapper around the Rust taffy UI layout library."""

from waxy._waxy import (
    AUTO,
    MAX_CONTENT,
    MIN_CONTENT,
    AlignContent,
    AlignItems,
    Auto,
    AvailableSize,
    BoxSizing,
    ChildIndexOutOfBounds,
    Definite,
    Display,
    FitContent,
    FlexDirection,
    FlexWrap,
    Fraction,
    GridAutoFlow,
    GridLine,
    GridPlacement,
    GridSpan,
    InvalidChildNode,
    InvalidGridLine,
    InvalidGridSpan,
    InvalidInputNode,
    InvalidLength,
    InvalidParentNode,
    InvalidPercent,
    KnownSize,
    Layout,
    Length,
    Line,
    MaxContent,
    MinContent,
    Minmax,
    NodeId,
    Overflow,
    Percent,
    Point,
    Position,
    Rect,
    Size,
    Style,
    TaffyException,
    TaffyTree,
    TextAlign,
    WaxyException,
)

type AvailableSpaceValue = Definite | MinContent | MaxContent
"""Available space value for measure functions: Definite, MinContent, or MaxContent."""

type DimensionValue = Length | Percent | Auto
"""A dimension value used for sizes, margins, insets, and flex-basis: Length, Percent, or Auto."""

type GridPlacementValue = GridLine | GridSpan | Auto
"""A grid placement value used in GridPlacement start and end: GridLine, GridSpan, or Auto."""

type GridTrackMaxValue = Length | Percent | Auto | MinContent | MaxContent | Fraction | FitContent
"""Maximum sizing bound for a Minmax grid track."""

type GridTrackMinValue = Length | Percent | Auto | MinContent | MaxContent
"""Minimum sizing bound for a Minmax grid track."""

type GridTrackValue = (
    Length | Percent | Auto | MinContent | MaxContent | Fraction | Minmax | FitContent
)
"""A grid track sizing value used in grid_template_* and grid_auto_* fields."""

type LengthPercentageValue = Length | Percent
"""A length-or-percentage value used for padding, border, and gap: Length or Percent."""

__all__ = [
    "AUTO",
    "MAX_CONTENT",
    "MIN_CONTENT",
    "AlignContent",
    "AlignItems",
    "Auto",
    "AvailableSize",
    "AvailableSpaceValue",
    "BoxSizing",
    "ChildIndexOutOfBounds",
    "Definite",
    "DimensionValue",
    "Display",
    "FitContent",
    "FlexDirection",
    "FlexWrap",
    "Fraction",
    "GridAutoFlow",
    "GridLine",
    "GridPlacement",
    "GridPlacementValue",
    "GridSpan",
    "GridTrackMaxValue",
    "GridTrackMinValue",
    "GridTrackValue",
    "InvalidChildNode",
    "InvalidGridLine",
    "InvalidGridSpan",
    "InvalidInputNode",
    "InvalidLength",
    "InvalidParentNode",
    "InvalidPercent",
    "KnownSize",
    "Layout",
    "Length",
    "LengthPercentageValue",
    "Line",
    "MaxContent",
    "MinContent",
    "Minmax",
    "NodeId",
    "Overflow",
    "Percent",
    "Point",
    "Position",
    "Rect",
    "Size",
    "Style",
    "TaffyException",
    "TaffyTree",
    "TextAlign",
    "WaxyException",
]
