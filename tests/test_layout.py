"""Tests for Layout's taffy-derived fields and helpers."""

import waxy


def padded_scroll_container() -> waxy.Layout:
    """A 100x50 scroll container with padding and border, holding a 300x200 child."""
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(waxy.Style(size_width=waxy.Length(300.0), size_height=waxy.Length(200.0)))
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Block,
            overflow_x=waxy.Overflow.Scroll,
            overflow_y=waxy.Overflow.Scroll,
            size_width=waxy.Length(100.0),
            size_height=waxy.Length(50.0),
            padding_left=waxy.Length(4.0),
            padding_top=waxy.Length(6.0),
            border_left=waxy.Length(1.0),
            border_top=waxy.Length(2.0),
        ),
        [child],
    )
    tree.compute_layout(root)
    return tree.layout(root)


def test_content_box_size() -> None:
    assert padded_scroll_container().content_box_size() == waxy.Size(95.0, 42.0)


def test_content_box_offsets() -> None:
    layout = padded_scroll_container()
    assert (layout.content_box_x(), layout.content_box_y()) == (5.0, 8.0)


def test_scrollable_overflow_rect_reaches_content_extent() -> None:
    rect = padded_scroll_container().scrollable_overflow_rect
    assert (rect.right, rect.bottom) == (304.0, 206.0)


def test_scroll_extent() -> None:
    layout = padded_scroll_container()
    assert (layout.scroll_width(), layout.scroll_height()) == (205.0, 158.0)


def test_scroll_extent_is_zero_without_overflow() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(size_width=waxy.Length(10.0)))
    tree.compute_layout(node)
    assert (tree.layout(node).scroll_width(), tree.layout(node).scroll_height()) == (0.0, 0.0)


def test_layout_eq_and_hash() -> None:
    a = padded_scroll_container()
    b = padded_scroll_container()
    assert a == b
    assert hash(a) == hash(b)
