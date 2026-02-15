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


def test_style_set_display() -> None:
    s = waxy.Style()
    s.display = waxy.Display.Block
    assert s.display == waxy.Display.Block


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


def test_style_repr() -> None:
    s = waxy.Style()
    assert "Style" in repr(s)
