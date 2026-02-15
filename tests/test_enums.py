import wax


def test_display_variants():
    assert wax.Display.Block is not None
    assert wax.Display.Flex is not None
    assert wax.Display.Grid is not None
    assert wax.Display.Nil is not None


def test_position_variants():
    assert wax.Position.Relative is not None
    assert wax.Position.Absolute is not None


def test_flex_direction_variants():
    assert wax.FlexDirection.Row is not None
    assert wax.FlexDirection.Column is not None
    assert wax.FlexDirection.RowReverse is not None
    assert wax.FlexDirection.ColumnReverse is not None


def test_flex_wrap_variants():
    assert wax.FlexWrap.NoWrap is not None
    assert wax.FlexWrap.Wrap is not None
    assert wax.FlexWrap.WrapReverse is not None


def test_align_items_variants():
    assert wax.AlignItems.Start is not None
    assert wax.AlignItems.End is not None
    assert wax.AlignItems.FlexStart is not None
    assert wax.AlignItems.FlexEnd is not None
    assert wax.AlignItems.Center is not None
    assert wax.AlignItems.Baseline is not None
    assert wax.AlignItems.Stretch is not None


def test_align_content_variants():
    assert wax.AlignContent.Start is not None
    assert wax.AlignContent.End is not None
    assert wax.AlignContent.Center is not None
    assert wax.AlignContent.Stretch is not None
    assert wax.AlignContent.SpaceBetween is not None
    assert wax.AlignContent.SpaceEvenly is not None
    assert wax.AlignContent.SpaceAround is not None


def test_overflow_variants():
    assert wax.Overflow.Visible is not None
    assert wax.Overflow.Clip is not None
    assert wax.Overflow.Hidden is not None
    assert wax.Overflow.Scroll is not None


def test_grid_auto_flow_variants():
    assert wax.GridAutoFlow.Row is not None
    assert wax.GridAutoFlow.Column is not None
    assert wax.GridAutoFlow.RowDense is not None
    assert wax.GridAutoFlow.ColumnDense is not None


def test_box_sizing_variants():
    assert wax.BoxSizing.BorderBox is not None
    assert wax.BoxSizing.ContentBox is not None


def test_text_align_variants():
    assert wax.TextAlign.Auto is not None
    assert wax.TextAlign.LegacyLeft is not None
    assert wax.TextAlign.LegacyRight is not None
    assert wax.TextAlign.LegacyCenter is not None


def test_available_space():
    d = wax.AvailableSpace.definite(100.0)
    assert d.is_definite()

    mc = wax.AvailableSpace.min_content()
    assert not mc.is_definite()

    mx = wax.AvailableSpace.max_content()
    assert not mx.is_definite()


def test_enum_equality():
    assert wax.Display.Flex == wax.Display.Flex
    assert wax.Display.Flex != wax.Display.Grid
