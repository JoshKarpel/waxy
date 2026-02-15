import wax


def test_style_default():
    s = wax.Style()
    assert s.display == wax.Display.Flex  # taffy default
    assert s.position == wax.Position.Relative
    assert s.flex_grow == 0.0
    assert s.flex_shrink == 1.0


def test_style_display():
    s = wax.Style(display=wax.Display.Grid)
    assert s.display == wax.Display.Grid


def test_style_set_display():
    s = wax.Style()
    s.display = wax.Display.Block
    assert s.display == wax.Display.Block


def test_style_flex_properties():
    s = wax.Style(
        flex_direction=wax.FlexDirection.Column,
        flex_wrap=wax.FlexWrap.Wrap,
        flex_grow=2.0,
        flex_shrink=0.5,
    )
    assert s.flex_direction == wax.FlexDirection.Column
    assert s.flex_wrap == wax.FlexWrap.Wrap
    assert s.flex_grow == 2.0
    assert s.flex_shrink == 0.5


def test_style_size():
    s = wax.Style(
        size_width=wax.Dimension.length(100.0),
        size_height=wax.Dimension.percent(0.5),
    )
    assert s.size_width == wax.Dimension.length(100.0)
    assert s.size_height == wax.Dimension.percent(0.5)


def test_style_padding():
    s = wax.Style(
        padding_left=wax.LengthPercentage.length(10.0),
        padding_right=wax.LengthPercentage.length(10.0),
        padding_top=wax.LengthPercentage.length(5.0),
        padding_bottom=wax.LengthPercentage.length(5.0),
    )
    assert s.padding_left == wax.LengthPercentage.length(10.0)
    assert s.padding_top == wax.LengthPercentage.length(5.0)


def test_style_margin():
    s = wax.Style(
        margin_left=wax.LengthPercentageAuto.length(10.0),
        margin_right=wax.LengthPercentageAuto.auto(),
    )
    assert s.margin_left == wax.LengthPercentageAuto.length(10.0)
    assert s.margin_right.is_auto()


def test_style_alignment():
    s = wax.Style(
        align_items=wax.AlignItems.Center,
        justify_content=wax.AlignContent.SpaceBetween,
    )
    assert s.align_items == wax.AlignItems.Center
    assert s.justify_content == wax.AlignContent.SpaceBetween


def test_style_alignment_none():
    s = wax.Style()
    assert s.align_items is None
    assert s.align_content is None


def test_style_grid():
    s = wax.Style(
        display=wax.Display.Grid,
        grid_template_columns=[
            wax.GridTrack.length(100.0),
            wax.GridTrack.flex(1.0),
        ],
    )
    assert s.display == wax.Display.Grid
    cols = s.grid_template_columns
    assert len(cols) == 2


def test_style_repr():
    s = wax.Style()
    assert "Style" in repr(s)
