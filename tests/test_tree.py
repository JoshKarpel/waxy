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
    node = tree.new_leaf(waxy.Style(size_width=waxy.Dimension.length(100.0)))
    assert tree.dirty(node)
    tree.compute_layout(node)
    assert not tree.dirty(node)
    tree.mark_dirty(node)
    assert tree.dirty(node)


def test_compute_layout() -> None:
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Dimension.length(100.0),
        size_height=waxy.Dimension.length(50.0),
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
        size_width=waxy.Dimension.length(100.0),
        size_height=waxy.Dimension.length(50.0),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(
        node,
        waxy.AvailableSpace.definite(200.0),
        waxy.AvailableSpace.definite(200.0),
    )
    layout = tree.layout(node)
    assert layout.size.width == 100.0
    assert layout.size.height == 50.0


def test_rounding() -> None:
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Dimension.length(10.5),
        size_height=waxy.Dimension.length(20.3),
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
    assert n1 == n1
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
