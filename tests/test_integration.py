import wax


def test_flexbox_row() -> None:
    """Three children in a row, each 100px wide in a 300px container."""
    tree = wax.TaffyTree()

    child_style = wax.Style(
        size_width=wax.Dimension.length(100.0),
        size_height=wax.Dimension.length(50.0),
    )

    c1 = tree.new_leaf(child_style)
    c2 = tree.new_leaf(child_style)
    c3 = tree.new_leaf(child_style)

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            flex_direction=wax.FlexDirection.Row,
            size_width=wax.Dimension.length(300.0),
            size_height=wax.Dimension.length(50.0),
        ),
        [c1, c2, c3],
    )

    tree.compute_layout(parent)

    l1 = tree.layout(c1)
    l2 = tree.layout(c2)
    l3 = tree.layout(c3)

    assert l1.location.x == 0.0
    assert l2.location.x == 100.0
    assert l3.location.x == 200.0

    assert l1.size.width == 100.0
    assert l2.size.width == 100.0
    assert l3.size.width == 100.0


def test_flexbox_column() -> None:
    """Children stacked in a column."""
    tree = wax.TaffyTree()

    child_style = wax.Style(
        size_width=wax.Dimension.length(100.0),
        size_height=wax.Dimension.length(30.0),
    )

    c1 = tree.new_leaf(child_style)
    c2 = tree.new_leaf(child_style)

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            flex_direction=wax.FlexDirection.Column,
            size_width=wax.Dimension.length(100.0),
        ),
        [c1, c2],
    )

    tree.compute_layout(parent)

    l1 = tree.layout(c1)
    l2 = tree.layout(c2)

    assert l1.location.y == 0.0
    assert l2.location.y == 30.0


def test_flex_grow() -> None:
    """Two children with flex_grow in a 300px container."""
    tree = wax.TaffyTree()

    c1 = tree.new_leaf(wax.Style(flex_grow=1.0, size_height=wax.Dimension.length(50.0)))
    c2 = tree.new_leaf(wax.Style(flex_grow=2.0, size_height=wax.Dimension.length(50.0)))

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            size_width=wax.Dimension.length(300.0),
            size_height=wax.Dimension.length(50.0),
        ),
        [c1, c2],
    )

    tree.compute_layout(parent)

    l1 = tree.layout(c1)
    l2 = tree.layout(c2)

    assert l1.size.width == 100.0  # 1/3 of 300
    assert l2.size.width == 200.0  # 2/3 of 300


def test_grid_layout() -> None:
    """Simple 2-column grid layout."""
    tree = wax.TaffyTree()

    c1 = tree.new_leaf(wax.Style(size_height=wax.Dimension.length(40.0)))
    c2 = tree.new_leaf(wax.Style(size_height=wax.Dimension.length(40.0)))

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Grid,
            size_width=wax.Dimension.length(200.0),
            grid_template_columns=[
                wax.GridTrack.length(100.0),
                wax.GridTrack.length(100.0),
            ],
        ),
        [c1, c2],
    )

    tree.compute_layout(parent)

    l1 = tree.layout(c1)
    l2 = tree.layout(c2)

    assert l1.location.x == 0.0
    assert l1.size.width == 100.0
    assert l2.location.x == 100.0
    assert l2.size.width == 100.0


def test_nested_layout() -> None:
    """Nested flex containers."""
    tree = wax.TaffyTree()

    leaf1 = tree.new_leaf(
        wax.Style(
            size_width=wax.Dimension.length(50.0),
            size_height=wax.Dimension.length(50.0),
        )
    )
    leaf2 = tree.new_leaf(
        wax.Style(
            size_width=wax.Dimension.length(50.0),
            size_height=wax.Dimension.length(50.0),
        )
    )

    inner = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            flex_direction=wax.FlexDirection.Column,
        ),
        [leaf1, leaf2],
    )

    outer_leaf = tree.new_leaf(
        wax.Style(
            size_width=wax.Dimension.length(100.0),
            size_height=wax.Dimension.length(100.0),
        )
    )

    root = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            flex_direction=wax.FlexDirection.Row,
            size_width=wax.Dimension.length(200.0),
        ),
        [inner, outer_leaf],
    )

    tree.compute_layout(root)

    inner_layout = tree.layout(inner)
    assert inner_layout.location.x == 0.0

    outer_leaf_layout = tree.layout(outer_leaf)
    assert outer_leaf_layout.location.x == 50.0

    leaf1_layout = tree.layout(leaf1)
    leaf2_layout = tree.layout(leaf2)
    assert leaf1_layout.location.y == 0.0
    assert leaf2_layout.location.y == 50.0


def test_padding_and_border() -> None:
    """Padding and border affect content box."""
    tree = wax.TaffyTree()

    child = tree.new_leaf(wax.Style(flex_grow=1.0))

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            size_width=wax.Dimension.length(100.0),
            size_height=wax.Dimension.length(100.0),
            padding_left=wax.LengthPercentage.length(10.0),
            padding_right=wax.LengthPercentage.length(10.0),
            padding_top=wax.LengthPercentage.length(5.0),
            padding_bottom=wax.LengthPercentage.length(5.0),
        ),
        [child],
    )

    tree.compute_layout(parent)

    child_layout = tree.layout(child)
    assert child_layout.size.width == 80.0  # 100 - 10 - 10
    assert child_layout.size.height == 90.0  # 100 - 5 - 5
    assert child_layout.location.x == 10.0
    assert child_layout.location.y == 5.0


def test_absolute_positioning() -> None:
    """Absolute positioning removes from flow."""
    tree = wax.TaffyTree()

    abs_child = tree.new_leaf(
        wax.Style(
            position=wax.Position.Absolute,
            size_width=wax.Dimension.length(50.0),
            size_height=wax.Dimension.length(50.0),
            inset_left=wax.LengthPercentageAuto.length(10.0),
            inset_top=wax.LengthPercentageAuto.length(10.0),
        )
    )

    parent = tree.new_with_children(
        wax.Style(
            display=wax.Display.Flex,
            size_width=wax.Dimension.length(200.0),
            size_height=wax.Dimension.length(200.0),
        ),
        [abs_child],
    )

    tree.compute_layout(parent)

    layout = tree.layout(abs_child)
    assert layout.location.x == 10.0
    assert layout.location.y == 10.0
    assert layout.size.width == 50.0
