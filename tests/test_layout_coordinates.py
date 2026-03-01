"""
Tests verifying Layout's border-box coordinate system.

Layout.location is relative to the parent's border box origin (not content box).
Layout.size is the border box size (excludes margin, includes border + padding + content).
"""

import waxy


def test_child_offset_by_parent_padding() -> None:
    """Child location is offset by parent's padding (location is relative to parent border box)."""
    tree = waxy.TaffyTree()

    child = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(50.0),
            size_height=waxy.Length(50.0),
        )
    )

    parent = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
            padding_left=waxy.Length(20.0),
            padding_top=waxy.Length(15.0),
        ),
        [child],
    )

    tree.compute_layout(parent)

    child_layout = tree.layout(child)

    # Location is relative to parent's border box, so it's offset by parent's padding.
    assert child_layout.location.x == 20.0
    assert child_layout.location.y == 15.0


def test_child_offset_by_own_margin() -> None:
    """Child location is offset by its own margin; size excludes margin."""
    tree = waxy.TaffyTree()

    child = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(50.0),
            size_height=waxy.Length(50.0),
            margin_left=waxy.Length(10.0),
            margin_top=waxy.Length(8.0),
        )
    )

    parent = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
        ),
        [child],
    )

    tree.compute_layout(parent)

    child_layout = tree.layout(child)

    # Location points to the border box origin, pushed inward by margin.
    assert child_layout.location.x == 10.0
    assert child_layout.location.y == 8.0

    # Size is the border box — margin is not included.
    assert child_layout.size.width == 50.0
    assert child_layout.size.height == 50.0

    # The margin values are available on the layout.
    assert child_layout.margin.left == 10.0
    assert child_layout.margin.top == 8.0


def test_child_offset_by_parent_border() -> None:
    """Child location is offset by parent's border + padding widths."""
    tree = waxy.TaffyTree()

    child = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(50.0),
            size_height=waxy.Length(50.0),
        )
    )

    parent = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
            border_left=waxy.Length(5.0),
            border_top=waxy.Length(3.0),
            padding_left=waxy.Length(10.0),
            padding_top=waxy.Length(7.0),
        ),
        [child],
    )

    tree.compute_layout(parent)

    child_layout = tree.layout(child)

    # Location is relative to parent's border box origin,
    # so it's offset by parent's border + padding.
    assert child_layout.location.x == 5.0 + 10.0  # border + padding
    assert child_layout.location.y == 3.0 + 7.0  # border + padding


def test_nested_location_accumulates_to_absolute_position() -> None:
    """Accumulating location from root down gives absolute border box positions."""
    tree = waxy.TaffyTree()

    grandchild = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(20.0),
            size_height=waxy.Length(20.0),
        )
    )

    parent = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            padding_left=waxy.Length(12.0),
            padding_top=waxy.Length(8.0),
        ),
        [grandchild],
    )

    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
            padding_left=waxy.Length(10.0),
            padding_top=waxy.Length(5.0),
        ),
        [parent],
    )

    tree.compute_layout(root)

    root_layout = tree.layout(root)
    parent_layout = tree.layout(parent)
    grandchild_layout = tree.layout(grandchild)

    # Root location is (0, 0) — it's the layout root.
    assert root_layout.location.x == 0.0
    assert root_layout.location.y == 0.0

    # Parent is offset by root's padding.
    assert parent_layout.location.x == 10.0
    assert parent_layout.location.y == 5.0

    # Grandchild is offset by parent's padding (relative to parent's border box).
    assert grandchild_layout.location.x == 12.0
    assert grandchild_layout.location.y == 8.0

    # Absolute position of grandchild's border box =
    # root.location + parent.location + grandchild.location
    abs_x = root_layout.location.x + parent_layout.location.x + grandchild_layout.location.x
    abs_y = root_layout.location.y + parent_layout.location.y + grandchild_layout.location.y

    assert abs_x == 0.0 + 10.0 + 12.0  # = 22.0
    assert abs_y == 0.0 + 5.0 + 8.0  # = 13.0


def test_size_is_border_box() -> None:
    """Size includes border + padding + content, but not margin."""
    tree = waxy.TaffyTree()

    child = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(60.0),
            size_height=waxy.Length(40.0),
            padding_left=waxy.Length(5.0),
            padding_right=waxy.Length(5.0),
            border_left=waxy.Length(2.0),
            border_right=waxy.Length(2.0),
            margin_left=waxy.Length(10.0),
            margin_right=waxy.Length(10.0),
        )
    )

    parent = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
        ),
        [child],
    )

    tree.compute_layout(parent)

    child_layout = tree.layout(child)

    # Default box_sizing is BorderBox, so specified size IS the border box.
    assert child_layout.size.width == 60.0
    assert child_layout.size.height == 40.0

    # Content box = size - padding - border.
    assert child_layout.content_box_width() == 60.0 - 5.0 - 5.0 - 2.0 - 2.0  # = 46.0
    assert child_layout.content_box_height() == 40.0  # no vertical padding/border

    # Margin is reported but not included in size.
    assert child_layout.margin.left == 10.0
    assert child_layout.margin.right == 10.0


def test_layout_border_and_padding_fields() -> None:
    """Layout reports resolved border and padding widths."""
    tree = waxy.TaffyTree()

    node = tree.new_leaf(
        waxy.Style(
            size_width=waxy.Length(100.0),
            size_height=waxy.Length(100.0),
            border_left=waxy.Length(1.0),
            border_right=waxy.Length(2.0),
            border_top=waxy.Length(3.0),
            border_bottom=waxy.Length(4.0),
            padding_left=waxy.Length(5.0),
            padding_right=waxy.Length(6.0),
            padding_top=waxy.Length(7.0),
            padding_bottom=waxy.Length(8.0),
        )
    )

    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            size_width=waxy.Length(200.0),
            size_height=waxy.Length(200.0),
        ),
        [node],
    )

    tree.compute_layout(root)

    layout = tree.layout(node)

    assert layout.border.left == 1.0
    assert layout.border.right == 2.0
    assert layout.border.top == 3.0
    assert layout.border.bottom == 4.0

    assert layout.padding.left == 5.0
    assert layout.padding.right == 6.0
    assert layout.padding.top == 7.0
    assert layout.padding.bottom == 8.0


def test_layout_size_is_border_box_regardless_of_box_sizing() -> None:
    """
    Layout.size is always the border box, regardless of the box_sizing style.

    box_sizing only changes how the style's size input is interpreted:
    - BorderBox: style size = border box (layout.size matches style size)
    - ContentBox: style size = content box (layout.size = style size + padding + border)
    """
    tree = waxy.TaffyTree()

    border_box_child = tree.new_leaf(
        waxy.Style(
            box_sizing=waxy.BoxSizing.BorderBox,
            size_width=waxy.Length(100.0),
            size_height=waxy.Length(100.0),
            padding_left=waxy.Length(10.0),
            padding_right=waxy.Length(10.0),
        )
    )

    content_box_child = tree.new_leaf(
        waxy.Style(
            box_sizing=waxy.BoxSizing.ContentBox,
            size_width=waxy.Length(100.0),
            size_height=waxy.Length(100.0),
            padding_left=waxy.Length(10.0),
            padding_right=waxy.Length(10.0),
        )
    )

    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Flex,
            flex_direction=waxy.FlexDirection.Column,
            size_width=waxy.Length(300.0),
            size_height=waxy.Length(300.0),
        ),
        [border_box_child, content_box_child],
    )

    tree.compute_layout(root)

    bb_layout = tree.layout(border_box_child)
    cb_layout = tree.layout(content_box_child)

    # BorderBox: style size 100 IS the border box → layout.size = 100, content = 80
    assert bb_layout.size.width == 100.0
    assert bb_layout.content_box_width() == 80.0

    # ContentBox: style size 100 is content → layout.size = 120 (border box), content = 100
    assert cb_layout.size.width == 120.0
    assert cb_layout.content_box_width() == 100.0
