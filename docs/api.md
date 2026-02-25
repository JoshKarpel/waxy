# API Reference

## Tree

::: waxy.TaffyTree

## Style

::: waxy.Style

## Layout

::: waxy.Layout

## Node

::: waxy.NodeId

## Geometry

::: waxy.Size

::: waxy.Rect

::: waxy.Point

::: waxy.Line

::: waxy.KnownSize

::: waxy.AvailableSize

## Value types

::: waxy.Length

::: waxy.Percent

::: waxy.Auto

::: waxy.MinContent

::: waxy.MaxContent

::: waxy.Definite

::: waxy.Fraction

::: waxy.FitContent

::: waxy.Minmax

::: waxy.GridLine

::: waxy.GridSpan

::: waxy.GridPlacement

## Type aliases

::: waxy.DimensionValue

::: waxy.LengthPercentageValue

::: waxy.GridTrackValue

::: waxy.GridTrackMinValue

::: waxy.GridTrackMaxValue

::: waxy.GridPlacementValue

::: waxy.AvailableSpaceValue

## Enums

::: waxy.Display

::: waxy.Position

::: waxy.FlexDirection

::: waxy.FlexWrap

::: waxy.AlignItems

::: waxy.AlignContent

::: waxy.Overflow

::: waxy.GridAutoFlow

::: waxy.BoxSizing

::: waxy.TextAlign

## Exceptions

```
Exception
 ├── KeyError
 │    └── InvalidNodeId [TaffyException]
 ├── ValueError
 │    ├── InvalidPercent [WaxyException]
 │    ├── InvalidLength [WaxyException]
 │    ├── InvalidGridLine [WaxyException]
 │    └── InvalidGridSpan [WaxyException]
 └── WaxyException
      ├── InvalidPercent [ValueError]
      ├── InvalidLength [ValueError]
      ├── InvalidGridLine [ValueError]
      ├── InvalidGridSpan [ValueError]
      └── TaffyException
           ├── ChildIndexOutOfBounds
           ├── InvalidParentNode
           ├── InvalidChildNode
           ├── InvalidInputNode
           └── InvalidNodeId [KeyError]
```

::: waxy.WaxyException

::: waxy.TaffyException

::: waxy.InvalidPercent

::: waxy.InvalidLength

::: waxy.InvalidGridLine

::: waxy.InvalidGridSpan

::: waxy.InvalidNodeId

::: waxy.ChildIndexOutOfBounds

::: waxy.InvalidParentNode

::: waxy.InvalidChildNode

::: waxy.InvalidInputNode
