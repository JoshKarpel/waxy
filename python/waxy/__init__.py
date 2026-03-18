"""Waxy: A Python wrapper around the Rust taffy UI layout library."""

from waxy._waxy import (
    AUTO,
    MAX_CONTENT,
    MIN_CONTENT,
    Auto,
    AvailableSize,
    ChildIndexOutOfBounds,
    Definite,
    FitContent,
    Fraction,
    GridLine,
    GridPlacement,
    GridSpan,
    InvalidChildNode,
    InvalidGridLine,
    InvalidGridSpan,
    InvalidInputNode,
    InvalidLength,
    InvalidNodeId,
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
    Percent,
    Point,
    Rect,
    Size,
    Style,
    TaffyException,
    TaffyTree,
    WaxyException,
)
from waxy._waxy import (
    AlignContent as _AlignContent,
)
from waxy._waxy import (
    AlignItems as _AlignItems,
)
from waxy._waxy import (
    BoxSizing as _BoxSizing,
)
from waxy._waxy import (
    Display as _Display,
)
from waxy._waxy import (
    FlexDirection as _FlexDirection,
)
from waxy._waxy import (
    FlexWrap as _FlexWrap,
)
from waxy._waxy import (
    GridAutoFlow as _GridAutoFlow,
)
from waxy._waxy import (
    Overflow as _Overflow,
)
from waxy._waxy import (
    Position as _Position,
)
from waxy._waxy import (
    TextAlign as _TextAlign,
)


class _EnumProxy:
    """
    A proxy that makes a PyO3 enum class iterable at the class level.

    Variant attributes delegate to the underlying Rust enum class, so values
    passed to Rust functions are proper Rust enum instances.
    """

    def __init__(self, rust_cls: type) -> None:
        self._rust_cls = rust_cls
        self._variants: list = rust_cls.variants()
        # Map variant instances to their names via identity comparison
        self._variant_attrs: dict[str, object] = {}
        for name in dir(rust_cls):
            if not name.startswith("_"):
                val = getattr(rust_cls, name, None)
                if isinstance(val, rust_cls):
                    self._variant_attrs[name] = val
        self.__name__ = rust_cls.__name__
        self.__qualname__ = rust_cls.__qualname__
        self.__module__ = "waxy"
        self.__doc__ = rust_cls.__doc__ or ""

    def __getattr__(self, name: str) -> object:
        try:
            return self._variant_attrs[name]
        except KeyError:
            return getattr(self._rust_cls, name)

    def __iter__(self) -> object:
        return iter(self._variants)

    def __instancecheck__(self, instance: object) -> bool:
        return isinstance(instance, self._rust_cls)

    def __repr__(self) -> str:
        return repr(self._rust_cls)


AlignContent = _EnumProxy(_AlignContent)
AlignItems = _EnumProxy(_AlignItems)
BoxSizing = _EnumProxy(_BoxSizing)
Display = _EnumProxy(_Display)
FlexDirection = _EnumProxy(_FlexDirection)
FlexWrap = _EnumProxy(_FlexWrap)
GridAutoFlow = _EnumProxy(_GridAutoFlow)
Overflow = _EnumProxy(_Overflow)
Position = _EnumProxy(_Position)
TextAlign = _EnumProxy(_TextAlign)

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
    "InvalidNodeId",
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
