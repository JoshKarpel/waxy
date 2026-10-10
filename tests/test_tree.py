import math
import struct
from collections.abc import Callable

import pytest

import waxy


def test_create_tree() -> None:
    tree = waxy.TaffyTree()
    assert tree.total_node_count() == 0


def test_with_capacity() -> None:
    tree = waxy.TaffyTree.with_capacity(10)
    assert tree.total_node_count() == 0


def test_new_leaf() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    assert tree.total_node_count() == 1
    assert isinstance(node, waxy.NodeId)


def test_new_with_children() -> None:
    tree = waxy.TaffyTree()
    child1 = tree.new_leaf(waxy.Style())
    child2 = tree.new_leaf(waxy.Style())
    parent = tree.new_with_children(waxy.Style(), [child1, child2])
    assert tree.total_node_count() == 3
    children = tree.children(parent)
    assert len(children) == 2


def test_add_child() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    child = tree.new_leaf(waxy.Style())
    tree.add_child(parent, child)
    assert tree.child_count(parent) == 1


def test_remove_child() -> None:
    tree = waxy.TaffyTree()
    child = tree.new_leaf(waxy.Style())
    parent = tree.new_with_children(waxy.Style(), [child])
    tree.remove_child(parent, child)
    assert tree.child_count(parent) == 0


def test_set_children() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    c1 = tree.new_leaf(waxy.Style())
    c2 = tree.new_leaf(waxy.Style())
    tree.set_children(parent, [c1, c2])
    assert tree.child_count(parent) == 2


def test_child_at_index() -> None:
    tree = waxy.TaffyTree()
    c1 = tree.new_leaf(waxy.Style())
    c2 = tree.new_leaf(waxy.Style())
    parent = tree.new_with_children(waxy.Style(), [c1, c2])
    assert tree.child_at_index(parent, 0) == c1
    assert tree.child_at_index(parent, 1) == c2


def test_parent() -> None:
    tree = waxy.TaffyTree()
    child = tree.new_leaf(waxy.Style())
    parent = tree.new_with_children(waxy.Style(), [child])
    assert tree.parent(child) == parent
    assert tree.parent(parent) is None


def test_remove_node() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    assert tree.total_node_count() == 0


def test_clear() -> None:
    tree = waxy.TaffyTree()
    tree.new_leaf(waxy.Style())
    tree.new_leaf(waxy.Style())
    tree.clear()
    assert tree.total_node_count() == 0


def test_set_and_get_style() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(flex_grow=1.0))
    style = tree.style(node)
    assert style.flex_grow == 1.0

    tree.set_style(node, waxy.Style(flex_grow=2.0))
    style = tree.style(node)
    assert style.flex_grow == 2.0


def test_dirty() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(size_width=waxy.Length(100.0)))
    assert tree.dirty(node)
    tree.compute_layout(node)
    assert not tree.dirty(node)
    tree.mark_dirty(node)
    assert tree.dirty(node)


def test_compute_layout() -> None:
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Length(100.0),
        size_height=waxy.Length(50.0),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(node)
    layout = tree.layout(node)
    assert layout.size.width == 100.0
    assert layout.size.height == 50.0
    assert layout.location.x == 0.0
    assert layout.location.y == 0.0


def test_compute_layout_with_available_space() -> None:
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Length(100.0),
        size_height=waxy.Length(50.0),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(
        node,
        available=waxy.AvailableSize(
            waxy.Definite(200.0),
            waxy.Definite(200.0),
        ),
    )
    layout = tree.layout(node)
    assert layout.size.width == 100.0
    assert layout.size.height == 50.0


def test_rounding() -> None:
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Length(10.5),
        size_height=waxy.Length(20.3),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(node)

    rounded = tree.layout(node)
    unrounded = tree.unrounded_layout(node)

    assert rounded.size.width == 11.0  # rounded
    assert unrounded.size.width == 10.5  # original

    tree.disable_rounding()
    tree.compute_layout(node)
    layout = tree.layout(node)
    assert layout.size.width == 10.5


def test_node_id_eq_and_hash() -> None:
    tree = waxy.TaffyTree()
    n1 = tree.new_leaf(waxy.Style())
    n2 = tree.new_leaf(waxy.Style())
    assert n1 == n1  # noqa: PLR0124
    assert n1 != n2
    assert hash(n1) == hash(n1)
    assert hash(n1) != hash(n2)
    node_set = {n1, n2}
    assert len(node_set) == 2


def test_replace_child() -> None:
    tree = waxy.TaffyTree()
    c1 = tree.new_leaf(waxy.Style())
    c2 = tree.new_leaf(waxy.Style())
    parent = tree.new_with_children(waxy.Style(), [c1])
    tree.replace_child_at_index(parent, 0, c2)
    assert tree.child_at_index(parent, 0) == c2


def test_repr() -> None:
    tree = waxy.TaffyTree()
    assert "TaffyTree" in repr(tree)
    node = tree.new_leaf(waxy.Style())
    assert "NodeId" in repr(node)


def test_layout_eq() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(size_width=waxy.Length(100.0), size_height=waxy.Length(50.0)))
    tree.compute_layout(node)
    assert tree.layout(node) == tree.layout(node)


def test_layout_hash() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(size_width=waxy.Length(100.0), size_height=waxy.Length(50.0)))
    tree.compute_layout(node)
    layout = tree.layout(node)
    assert hash(layout) == hash(tree.layout(node))
    assert len({layout, tree.layout(node)}) == 1


def test_remove_children_range_detaches_children() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    children = [tree.new_leaf(waxy.Style()) for _ in range(4)]
    parent = tree.new_with_children(waxy.Style(), children)
    tree.remove_children_range(parent, 1, 3)
    assert tree.children(parent) == [children[0], children[3]]
    assert tree.parent(children[1]) is None
    assert tree.total_node_count() == 5


def test_remove_children_range_empty_range_is_noop() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    children = [tree.new_leaf(waxy.Style()) for _ in range(2)]
    parent = tree.new_with_children(waxy.Style(), children)
    tree.remove_children_range(parent, 1, 1)
    assert tree.children(parent) == children


@pytest.mark.parametrize(("start", "end"), [(0, 3), (2, 1)])
def test_remove_children_range_out_of_bounds_raises(start: int, end: int) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    parent = tree.new_with_children(waxy.Style(), [tree.new_leaf(waxy.Style()) for _ in range(2)])
    with pytest.raises(waxy.ChildIndexOutOfBounds):
        tree.remove_children_range(parent, start, end)


def test_set_style_with_equal_style_keeps_node_clean() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(flex_grow=1))
    tree.compute_layout(node)
    tree.set_style(node, waxy.Style(flex_grow=1))
    assert not tree.dirty(node)


def test_set_style_with_equal_values_but_different_set_fields_keeps_node_clean() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.compute_layout(node)
    tree.set_style(node, waxy.Style(display=waxy.Display.Flex))
    assert not tree.dirty(node)


def test_set_style_with_different_style_marks_node_dirty() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(flex_grow=1))
    tree.compute_layout(node)
    tree.set_style(node, waxy.Style(flex_grow=2))
    assert tree.dirty(node)


def test_set_style_on_removed_node_raises() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.set_style(node, waxy.Style())


def test_format_tree_includes_every_node_indented_by_depth() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    leaf = tree.new_leaf(waxy.Style(size_width=waxy.Length(3)))
    middle = tree.new_with_children(waxy.Style(padding_left=waxy.Length(1)), [leaf])
    root = tree.new_with_children(waxy.Style(), [middle])
    tree.compute_layout(root)

    assert tree.format_tree(root).splitlines() == [
        f"{root!r} location=Point(x=0, y=0) size=Size(width=4, height=0) Style()",
        (
            f"  {middle!r} location=Point(x=0, y=0) size=Size(width=4, height=0)"
            " Style(padding_left=Length(1))"
        ),
        (
            f"    {leaf!r} location=Point(x=1, y=0) size=Size(width=3, height=0)"
            " Style(size_width=Length(3))"
        ),
    ]


def test_format_tree_shows_a_nan_field_as_set() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(flex_grow=float("nan")))
    tree.compute_layout(node)
    assert tree.format_tree(node).endswith(" Style(flex_grow=nan)")


def test_format_tree_of_removed_node_raises() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.format_tree(node)


def build_nested_margins(tree: waxy.TaffyTree[object]) -> tuple[waxy.NodeId, ...]:
    """A root holding a parent holding two leaves, each offset by a 0.4px left margin."""
    first = tree.new_leaf(
        waxy.Style(
            margin_left=waxy.Length(0.4), size_width=waxy.Length(3), size_height=waxy.Length(2)
        )
    )
    second = tree.new_leaf(waxy.Style(size_width=waxy.Length(5), size_height=waxy.Length(1)))
    parent = tree.new_with_children(
        waxy.Style(margin_left=waxy.Length(0.4), margin_top=waxy.Length(1)), [first, second]
    )
    root = tree.new_with_children(waxy.Style(size_width=waxy.Length(20)), [parent])
    tree.compute_layout(root)
    return root, parent, first, second


def test_absolute_layouts_lists_subtree_in_pre_order() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root, parent, first, second = build_nested_margins(tree)
    assert [node for node, _, _ in tree.absolute_layouts(root)] == [root, parent, first, second]


def test_absolute_layouts_returns_layouts_unchanged() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root, *_ = build_nested_margins(tree)
    assert all(layout == tree.layout(node) for node, _, layout in tree.absolute_layouts(root))


def test_absolute_layouts_rounds_summed_unrounded_locations() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root, _, first, _ = build_nested_margins(tree)
    positions = {node: position for node, position, _ in tree.absolute_layouts(root)}

    # The leaf's unrounded absolute left edge is 0.4 + 0.4 = 0.8, and round(0.8) = 1.
    assert positions[first] == waxy.Point(1, 1)
    # The returned position plus the rounded size lands on the right edge taffy implies,
    # round(0.8 + 3) = 4.
    assert positions[first].x + tree.layout(first).size.width == 4


def test_summed_rounded_locations_disagree_with_rounded_sizes_in_taffy() -> None:
    """
    Pin taffy#834, the bug `absolute_layouts` works around, so the upgrade that fixes it fails here.

    taffy 0.14 rounds each `location` relative to its parent, so summing rounded locations gives
    round(0.4) + round(0.4) = 0, though taffy rounds the leaf's size against its absolute left
    edge, round(0.8) = 1.
    """
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root, parent, first, _ = build_nested_margins(tree)
    summed = tree.layout(root).location + tree.layout(parent).location + tree.layout(first).location
    absolute = {node: position for node, position, _ in tree.absolute_layouts(root)}[first]

    assert summed.x != absolute.x, (
        "taffy now rounds locations in cumulative coordinates (taffy#1189), so summing rounded "
        "locations is correct: delete this test and the taffy#834 notes in docs/changelog.md, "
        "docs/performance.md, plans/styling-foundations.md, absolute_layouts' docstring in "
        "python/waxy/__init__.pyi, and collect_absolute_layouts in src/tree.rs"
    )


def to_f32(value: float) -> float:
    """Round a Python float to the nearest f32, to redo taffy's f32 arithmetic exactly."""
    return float(struct.unpack("f", struct.pack("f", value))[0])


def round_like_taffy(value: float) -> float:
    """Taffy's pixel rounding: half up, so round(-0.5) is 0, unlike Rust's `f32::round`."""
    return float(math.floor(value + 0.5))


def fractional_leaf(width: float, margin: float) -> waxy.Style:
    return waxy.Style(
        size_width=waxy.Length(width),
        size_height=waxy.Length(width / 2),
        margin_left=waxy.Length(margin),
        margin_top=waxy.Length(margin / 2),
    )


def fractional_box(direction: waxy.FlexDirection, padding: float) -> waxy.Style:
    return waxy.Style(
        flex_direction=direction,
        padding_left=waxy.Length(padding),
        padding_top=waxy.Length(padding),
        border_left=waxy.Length(0.125),
        gap_width=waxy.Length(0.375),
        gap_height=waxy.Length(0.625),
    )


def nested_fractional_flex(tree: waxy.TaffyTree[object]) -> waxy.NodeId:
    """Nested rows and columns offset by fractional padding, borders, gaps and margins."""
    row, column = waxy.FlexDirection.Row, waxy.FlexDirection.Column
    first_row = tree.new_with_children(
        fractional_box(row, 0.375),
        [
            tree.new_leaf(fractional_leaf(2.375, 0.25)),
            tree.new_leaf(fractional_leaf(3.625, 0.5)),
            tree.new_leaf(fractional_leaf(1.125, 0.875)),
        ],
    )
    inner_column = tree.new_with_children(
        fractional_box(column, 0.125),
        [tree.new_leaf(fractional_leaf(4.25, 0.375)), tree.new_leaf(fractional_leaf(0.875, 0.625))],
    )
    second_row = tree.new_with_children(fractional_box(row, 0.875), [inner_column])
    return tree.new_with_children(fractional_box(column, 0.625), [first_row, second_row])


def negative_half_offsets(tree: waxy.TaffyTree[object]) -> waxy.NodeId:
    """Leaves pulled left and up by negative half-pixel margins, where rounding modes disagree."""
    leaves = [
        tree.new_leaf(fractional_leaf(width=3.0, margin=margin))
        for margin in (-0.5, -1.5, -2.5, -0.25)
    ]
    return tree.new_with_children(
        waxy.Style(flex_direction=waxy.FlexDirection.Column, padding_left=waxy.Length(0.0)),
        leaves,
    )


def exact_half_boundaries(tree: waxy.TaffyTree[object]) -> waxy.NodeId:
    """Every level offset by exactly half a pixel, so absolute edges alternate .5 and whole."""
    node = tree.new_leaf(fractional_leaf(width=2.5, margin=0.5))
    for _ in range(4):
        node = tree.new_with_children(
            waxy.Style(padding_left=waxy.Length(0.5), padding_top=waxy.Length(0.5)), [node]
        )
    return node


def fractional_grid_tracks(tree: waxy.TaffyTree[object]) -> waxy.NodeId:
    """A grid splitting 10px into thirds, whose track edges aren't exact in any binary float."""
    cells = [tree.new_leaf(waxy.Style()) for _ in range(6)]
    return tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            size_width=waxy.Length(10),
            size_height=waxy.Length(7),
            margin_left=waxy.Length(0.3),
            grid_template_columns=[waxy.Fraction(1)] * 3,
            grid_template_rows=[waxy.Fraction(1)] * 2,
            gap_width=waxy.Length(0.7),
        ),
        cells,
    )


def absolute_and_hidden_children(tree: waxy.TaffyTree[object]) -> waxy.NodeId:
    """An absolutely positioned child at fractional insets, and a `display: Nil` child."""
    positioned = tree.new_with_children(
        waxy.Style(
            position=waxy.Position.Absolute,
            inset_left=waxy.Length(1.45),
            inset_top=waxy.Length(2.55),
            size_width=waxy.Length(3.3),
            size_height=waxy.Length(1.1),
            padding_left=waxy.Length(0.45),
        ),
        [tree.new_leaf(fractional_leaf(width=1.6, margin=0.35))],
    )
    hidden = tree.new_with_children(
        waxy.Style(display=waxy.Display.Nil), [tree.new_leaf(fractional_leaf(1.0, 0.5))]
    )
    in_flow = tree.new_leaf(fractional_leaf(width=2.2, margin=0.65))
    return tree.new_with_children(
        waxy.Style(size_width=waxy.Length(12.7), padding_left=waxy.Length(0.15)),
        [positioned, hidden, in_flow],
    )


ROUNDING_TREES = [
    nested_fractional_flex,
    negative_half_offsets,
    exact_half_boundaries,
    fractional_grid_tracks,
    absolute_and_hidden_children,
]


def unrounded_absolute_positions(
    tree: waxy.TaffyTree[object], root: waxy.NodeId
) -> dict[waxy.NodeId, tuple[float, float]]:
    """Each node's unrounded absolute position, summed top-down in f32 as taffy's rounding does."""
    location = tree.unrounded_layout(root).location
    positions = {root: (location.x, location.y)}
    pending = [root]
    while pending:
        node = pending.pop()
        x, y = positions[node]
        for child in tree.children(node):
            location = tree.unrounded_layout(child).location
            positions[child] = (to_f32(x + location.x), to_f32(y + location.y))
            pending.append(child)
    return positions


@pytest.mark.parametrize("build", ROUNDING_TREES)
def test_absolute_layouts_positions_agree_with_taffy_rounded_sizes(
    build: Callable[[waxy.TaffyTree[object]], waxy.NodeId],
) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root = build(tree)
    tree.compute_layout(root)
    unrounded = unrounded_absolute_positions(tree, root)

    for node, position, layout in tree.absolute_layouts(root):
        left, top = unrounded[node]
        size = tree.unrounded_layout(node).size
        # taffy rounds a node's size as round(left + width) - round(left), so its rounded box
        # starts at round(left) and ends at round(left + width).
        assert (position.x, position.y) == (round_like_taffy(left), round_like_taffy(top))
        assert position.x + layout.size.width == round_like_taffy(to_f32(left + size.width))
        assert position.y + layout.size.height == round_like_taffy(to_f32(top + size.height))


@pytest.mark.parametrize("build", ROUNDING_TREES)
def test_absolute_layouts_without_rounding_are_unrounded_sums(
    build: Callable[[waxy.TaffyTree[object]], waxy.NodeId],
) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    tree.disable_rounding()
    root = build(tree)
    tree.compute_layout(root)
    unrounded = unrounded_absolute_positions(tree, root)

    for node, position, _ in tree.absolute_layouts(root):
        assert (position.x, position.y) == unrounded[node]


@pytest.mark.parametrize("build", ROUNDING_TREES)
def test_absolute_layouts_of_any_subtree_match_the_whole_tree(
    build: Callable[[waxy.TaffyTree[object]], waxy.NodeId],
) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root = build(tree)
    tree.compute_layout(root)
    whole = {node: position for node, position, _ in tree.absolute_layouts(root)}

    for subtree_root in whole:
        for node, position, _ in tree.absolute_layouts(subtree_root):
            assert position == whole[node]


def build_hidden_subtree(tree: waxy.TaffyTree[object]) -> tuple[waxy.NodeId, ...]:
    """A root holding a visible leaf, then a hidden node over a non-hidden child and grandchild."""
    grandchild = tree.new_leaf(waxy.Style(size_width=waxy.Length(2), size_height=waxy.Length(3)))
    child = tree.new_with_children(waxy.Style(padding_left=waxy.Length(1)), [grandchild])
    hidden = tree.new_with_children(waxy.Style(display=waxy.Display.Nil), [child])
    visible = tree.new_leaf(waxy.Style(size_width=waxy.Length(4), size_height=waxy.Length(5)))
    root = tree.new_with_children(waxy.Style(size_width=waxy.Length(20)), [visible, hidden])
    tree.compute_layout(root)
    return root, visible, hidden, child, grandchild


def test_absolute_layouts_leaves_out_hidden_subtrees() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root, visible, *_ = build_hidden_subtree(tree)
    assert [node for node, _, _ in tree.absolute_layouts(root)] == [root, visible]


@pytest.mark.parametrize("index", [2, 3, 4], ids=["hidden", "child", "grandchild"])
def test_absolute_layouts_inside_hidden_subtree_is_empty(index: int) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    subtree_root = build_hidden_subtree(tree)[index]
    assert tree.absolute_layouts(subtree_root) == []


def test_absolute_layouts_of_removed_node_raises() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.absolute_layouts(node)
