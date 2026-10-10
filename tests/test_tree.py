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


def test_format_tree_of_removed_node_raises() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    with pytest.raises(waxy.InvalidNodeId):
        tree.format_tree(node)
