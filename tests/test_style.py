import pytest

import waxy


def test_style_default() -> None:
    s = waxy.Style()
    assert s.display == waxy.Display.Flex  # taffy default
    assert s.position == waxy.Position.Relative
    assert s.flex_grow == 0.0
    assert s.flex_shrink == 1.0


def test_style_display() -> None:
    s = waxy.Style(display=waxy.Display.Grid)
    assert s.display == waxy.Display.Grid


def test_style_immutable() -> None:
    s = waxy.Style()
    with pytest.raises(AttributeError):
        setattr(s, "display", waxy.Display.Block)


def test_style_flex_properties() -> None:
    s = waxy.Style(
        flex_direction=waxy.FlexDirection.Column,
        flex_wrap=waxy.FlexWrap.Wrap,
        flex_grow=2.0,
        flex_shrink=0.5,
    )
    assert s.flex_direction == waxy.FlexDirection.Column
    assert s.flex_wrap == waxy.FlexWrap.Wrap
    assert s.flex_grow == 2.0
    assert s.flex_shrink == 0.5


def test_style_size() -> None:
    s = waxy.Style(
        size_width=waxy.Dimension.length(100.0),
        size_height=waxy.Dimension.percent(0.5),
    )
    assert s.size_width == waxy.Dimension.length(100.0)
    assert s.size_height == waxy.Dimension.percent(0.5)


def test_style_padding() -> None:
    s = waxy.Style(
        padding_left=waxy.LengthPercentage.length(10.0),
        padding_right=waxy.LengthPercentage.length(10.0),
        padding_top=waxy.LengthPercentage.length(5.0),
        padding_bottom=waxy.LengthPercentage.length(5.0),
    )
    assert s.padding_left == waxy.LengthPercentage.length(10.0)
    assert s.padding_top == waxy.LengthPercentage.length(5.0)


def test_style_margin() -> None:
    s = waxy.Style(
        margin_left=waxy.LengthPercentageAuto.length(10.0),
        margin_right=waxy.LengthPercentageAuto.auto(),
    )
    assert s.margin_left == waxy.LengthPercentageAuto.length(10.0)
    assert s.margin_right.is_auto()


def test_style_alignment() -> None:
    s = waxy.Style(
        align_items=waxy.AlignItems.Center,
        justify_content=waxy.AlignContent.SpaceBetween,
    )
    assert s.align_items == waxy.AlignItems.Center
    assert s.justify_content == waxy.AlignContent.SpaceBetween


def test_style_alignment_none() -> None:
    s = waxy.Style()
    assert s.align_items is None
    assert s.align_content is None


def test_style_grid() -> None:
    s = waxy.Style(
        display=waxy.Display.Grid,
        grid_template_columns=[
            waxy.GridTrack.length(100.0),
            waxy.GridTrack.flex(1.0),
        ],
    )
    assert s.display == waxy.Display.Grid
    cols = s.grid_template_columns
    assert len(cols) == 2


def test_style_none_uses_default() -> None:
    s = waxy.Style(display=None)
    assert s.display == waxy.Display.Flex  # taffy default


def test_style_or_rhs_overrides_lhs() -> None:
    a = waxy.Style(display=waxy.Display.Flex, flex_grow=1.0)
    b = waxy.Style(display=waxy.Display.Grid)
    result = a | b
    assert result.display == waxy.Display.Grid
    assert result.flex_grow == 1.0  # preserved from a


def test_style_or_unset_fields_not_overridden() -> None:
    a = waxy.Style(flex_grow=2.0, flex_shrink=0.5)
    b = waxy.Style(flex_grow=3.0)
    result = a | b
    assert result.flex_grow == 3.0  # overridden by b
    assert result.flex_shrink == 0.5  # preserved from a


def test_style_or_empty_rhs_preserves_lhs() -> None:
    a = waxy.Style(display=waxy.Display.Block, position=waxy.Position.Absolute)
    b = waxy.Style()
    result = a | b
    assert result.display == waxy.Display.Block
    assert result.position == waxy.Position.Absolute


def test_style_or_chaining() -> None:
    a = waxy.Style(display=waxy.Display.Flex)
    b = waxy.Style(flex_grow=1.0)
    c = waxy.Style(flex_shrink=0.0)
    result = a | b | c
    assert result.display == waxy.Display.Flex
    assert result.flex_grow == 1.0
    assert result.flex_shrink == 0.0


def test_style_or_alignment_fields() -> None:
    a = waxy.Style(align_items=waxy.AlignItems.Center)
    b = waxy.Style(justify_content=waxy.AlignContent.SpaceBetween)
    result = a | b
    assert result.align_items == waxy.AlignItems.Center
    assert result.justify_content == waxy.AlignContent.SpaceBetween


def test_style_or_size_fields() -> None:
    a = waxy.Style(
        size_width=waxy.Dimension.length(100.0),
        size_height=waxy.Dimension.length(200.0),
    )
    b = waxy.Style(size_width=waxy.Dimension.percent(0.5))
    result = a | b
    assert result.size_width == waxy.Dimension.percent(0.5)
    assert result.size_height == waxy.Dimension.length(200.0)


def test_style_or_does_not_mutate_operands() -> None:
    a = waxy.Style(display=waxy.Display.Flex)
    b = waxy.Style(display=waxy.Display.Grid)
    _ = a | b
    assert a.display == waxy.Display.Flex
    assert b.display == waxy.Display.Grid


def test_style_or_default_value_overrides_when_explicit() -> None:
    """Setting a field to its default value explicitly should still override."""
    a = waxy.Style(flex_grow=2.0)
    b = waxy.Style(flex_grow=0.0)  # 0.0 is the default, but explicitly set
    result = a | b
    assert result.flex_grow == 0.0


def test_style_or_explicit_none_clears_field() -> None:
    """Passing None explicitly should clear the field in the merged result."""
    a = waxy.Style(align_items=waxy.AlignItems.Center)
    b = waxy.Style(align_items=None)
    result = a | b
    assert result.align_items is None


def test_style_or_explicit_none_aspect_ratio() -> None:
    """Passing aspect_ratio=None explicitly should clear it."""
    a = waxy.Style(aspect_ratio=1.5)
    b = waxy.Style(aspect_ratio=None)
    result = a | b
    assert result.aspect_ratio is None


def test_style_or_grid_tracks() -> None:
    a = waxy.Style(
        grid_template_columns=[waxy.GridTrack.length(100.0)],
    )
    b = waxy.Style(
        grid_template_rows=[waxy.GridTrack.flex(1.0)],
    )
    result = a | b
    assert len(result.grid_template_columns) == 1
    assert len(result.grid_template_rows) == 1


def test_style_repr() -> None:
    s = waxy.Style()
    assert "Style" in repr(s)
