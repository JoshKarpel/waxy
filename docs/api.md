# API Reference

## Tree

::: waxy.TaffyTree

## Style

::: waxy.Style

## Layout

::: waxy.Layout

::: waxy.DetailedGridInfo

::: waxy.DetailedGridTracksInfo

::: waxy.DetailedGridItemInfo

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

::: waxy.Stretch

::: waxy.FitContentKeyword

::: waxy.Content

::: waxy.Definite

::: waxy.Fraction

::: waxy.FitContent

::: waxy.Minmax

::: waxy.Repeat

::: waxy.AutoFill

::: waxy.AutoFit

::: waxy.GridLine

::: waxy.GridSpan

::: waxy.NamedGridLine

::: waxy.NamedGridSpan

::: waxy.GridPlacement

::: waxy.GridTemplateArea

::: waxy.GridTemplateAreas

## Constants

::: waxy.AUTO

::: waxy.MIN_CONTENT

::: waxy.MAX_CONTENT

::: waxy.STRETCH

::: waxy.FIT_CONTENT

::: waxy.CONTENT

::: waxy.AUTO_FILL

::: waxy.AUTO_FIT

## Type aliases

::: waxy.DimensionValue

::: waxy.FlexBasisValue

::: waxy.LengthPercentageAutoValue

::: waxy.LengthPercentageValue

::: waxy.GridTrackValue

::: waxy.GridTemplateValue

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

::: waxy.Direction

::: waxy.Float

::: waxy.Clear

::: waxy.Contain

## Exceptions

```
Exception
 ├── KeyError
 │    └── InvalidNodeId [TaffyException]
 ├── ValueError
 │    ├── InvalidPercent [WaxyException]
 │    ├── InvalidLength [WaxyException]
 │    ├── InvalidGridLine [WaxyException]
 │    ├── InvalidGridSpan [WaxyException]
 │    ├── InvalidFlexLineCount [WaxyException]
 │    ├── InvalidRepeat [WaxyException]
 │    ├── InvalidGridTemplateArea [WaxyException]
 │    └── InvalidGridTemplateAreas [WaxyException]
 └── WaxyException
      ├── InvalidPercent [ValueError]
      ├── InvalidLength [ValueError]
      ├── InvalidGridLine [ValueError]
      ├── InvalidGridSpan [ValueError]
      ├── InvalidFlexLineCount [ValueError]
      ├── InvalidRepeat [ValueError]
      ├── InvalidGridTemplateArea [ValueError]
      ├── InvalidGridTemplateAreas [ValueError]
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

::: waxy.InvalidFlexLineCount

::: waxy.InvalidRepeat

::: waxy.InvalidGridTemplateArea

::: waxy.InvalidGridTemplateAreas

::: waxy.InvalidNodeId

::: waxy.ChildIndexOutOfBounds

::: waxy.InvalidParentNode

::: waxy.InvalidChildNode

::: waxy.InvalidInputNode
