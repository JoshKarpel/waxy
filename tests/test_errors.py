import pytest

import waxy

TAFFY_EXCEPTION_SUBCLASSES = [
    waxy.ChildIndexOutOfBounds,
    waxy.InvalidParentNode,
    waxy.InvalidChildNode,
    waxy.InvalidInputNode,
    waxy.InvalidNodeId,
]


def test_waxy_exception_base() -> None:
    assert issubclass(waxy.WaxyException, Exception)


def test_taffy_exception_is_waxy_exception() -> None:
    assert issubclass(waxy.TaffyException, waxy.WaxyException)


def test_taffy_exception_is_exception() -> None:
    assert issubclass(waxy.TaffyException, Exception)


@pytest.mark.parametrize(
    "exc_class",
    TAFFY_EXCEPTION_SUBCLASSES,
    ids=[cls.__name__ for cls in TAFFY_EXCEPTION_SUBCLASSES],
)
def test_taffy_exception_hierarchy(exc_class: type) -> None:
    assert issubclass(exc_class, waxy.TaffyException)


@pytest.mark.parametrize(
    "exc_class",
    TAFFY_EXCEPTION_SUBCLASSES,
    ids=[cls.__name__ for cls in TAFFY_EXCEPTION_SUBCLASSES],
)
def test_waxy_exception_hierarchy(exc_class: type) -> None:
    assert issubclass(exc_class, waxy.WaxyException)


def test_invalid_percent_is_waxy_exception() -> None:
    assert issubclass(waxy.InvalidPercent, waxy.WaxyException)


def test_invalid_percent_is_value_error() -> None:
    assert issubclass(waxy.InvalidPercent, ValueError)


def test_invalid_percent_raised_above_range() -> None:
    with pytest.raises(waxy.InvalidPercent):
        waxy.Percent(1.5)


def test_invalid_percent_raised_below_range() -> None:
    with pytest.raises(waxy.InvalidPercent):
        waxy.Percent(-0.1)


def test_invalid_percent_catchable_as_value_error() -> None:
    with pytest.raises(ValueError, match="must be in"):
        waxy.Percent(2.0)


def test_invalid_percent_catchable_as_waxy_exception() -> None:
    with pytest.raises(waxy.WaxyException):
        waxy.Percent(-1.0)


def test_invalid_length_is_waxy_exception() -> None:
    assert issubclass(waxy.InvalidLength, waxy.WaxyException)


def test_invalid_length_is_value_error() -> None:
    assert issubclass(waxy.InvalidLength, ValueError)


def test_invalid_length_raised_for_nan() -> None:
    with pytest.raises(waxy.InvalidLength, match="NaN"):
        waxy.Length(float("nan"))


def test_invalid_length_catchable_as_value_error() -> None:
    with pytest.raises(ValueError, match="NaN"):
        waxy.Length(float("nan"))


def test_invalid_length_catchable_as_waxy_exception() -> None:
    with pytest.raises(waxy.WaxyException):
        waxy.Length(float("nan"))


def test_invalid_grid_line_is_waxy_exception() -> None:
    assert issubclass(waxy.InvalidGridLine, waxy.WaxyException)


def test_invalid_grid_line_is_value_error() -> None:
    assert issubclass(waxy.InvalidGridLine, ValueError)


def test_invalid_grid_line_raised_for_zero() -> None:
    with pytest.raises(waxy.InvalidGridLine, match="0"):
        waxy.GridLine(0)


def test_invalid_grid_line_catchable_as_value_error() -> None:
    with pytest.raises(ValueError, match="0"):
        waxy.GridLine(0)


def test_invalid_grid_line_catchable_as_waxy_exception() -> None:
    with pytest.raises(waxy.WaxyException):
        waxy.GridLine(0)


def test_invalid_grid_span_is_waxy_exception() -> None:
    assert issubclass(waxy.InvalidGridSpan, waxy.WaxyException)


def test_invalid_grid_span_is_value_error() -> None:
    assert issubclass(waxy.InvalidGridSpan, ValueError)


def test_invalid_grid_span_raised_for_zero() -> None:
    with pytest.raises(waxy.InvalidGridSpan, match="at least 1"):
        waxy.GridSpan(0)


def test_invalid_grid_span_catchable_as_value_error() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        waxy.GridSpan(0)


def test_invalid_grid_span_catchable_as_waxy_exception() -> None:
    with pytest.raises(waxy.WaxyException):
        waxy.GridSpan(0)


def test_child_index_out_of_bounds() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.ChildIndexOutOfBounds):
        tree.child_at_index(parent, 0)


def test_catch_taffy_base_exception() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.TaffyException):
        tree.child_at_index(parent, 99)


def test_catch_waxy_base_exception() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.WaxyException):
        tree.child_at_index(parent, 99)


# --- InvalidNodeId hierarchy tests ---


def test_invalid_node_id_is_taffy_exception() -> None:
    assert issubclass(waxy.InvalidNodeId, waxy.TaffyException)


def test_invalid_node_id_is_key_error() -> None:
    assert issubclass(waxy.InvalidNodeId, KeyError)


def test_invalid_node_id_is_exception() -> None:
    assert issubclass(waxy.InvalidNodeId, Exception)


# --- InvalidNodeId behavioral tests (one per panicking method) ---


def _removed_node() -> tuple[waxy.TaffyTree, waxy.NodeId]:
    """Helper: create a tree, add a node, remove it, return both."""
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    return tree, node


def test_invalid_node_id_children() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.children(node)


def test_invalid_node_id_child_count() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.child_count(node)


def test_invalid_node_id_parent() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.parent(node)


def test_invalid_node_id_style() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.style(node)


def test_invalid_node_id_set_style() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.set_style(node, waxy.Style())


def test_invalid_node_id_layout() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.layout(node)


def test_invalid_node_id_unrounded_layout() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.unrounded_layout(node)


def test_invalid_node_id_mark_dirty() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.mark_dirty(node)


def test_invalid_node_id_dirty() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.dirty(node)


def test_invalid_node_id_set_node_context() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.set_node_context(node, "ctx")


def test_invalid_node_id_remove_double() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.remove(node)


def test_invalid_node_id_add_child() -> None:
    tree, node = _removed_node()
    live = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.InvalidNodeId):
        tree.add_child(node, live)


def test_invalid_node_id_add_child_invalid_child() -> None:
    tree, node = _removed_node()
    live = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.InvalidNodeId):
        tree.add_child(live, node)


def test_invalid_node_id_insert_child_at_index() -> None:
    tree, node = _removed_node()
    live = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.InvalidNodeId):
        tree.insert_child_at_index(node, 0, live)


def test_invalid_node_id_set_children() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.set_children(node, [])


def test_invalid_node_id_remove_child() -> None:
    tree, node = _removed_node()
    live = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.InvalidNodeId):
        tree.remove_child(node, live)


def test_invalid_node_id_remove_child_at_index() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.remove_child_at_index(node, 0)


def test_invalid_node_id_replace_child_at_index() -> None:
    tree, node = _removed_node()
    live = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.InvalidNodeId):
        tree.replace_child_at_index(node, 0, live)


def test_invalid_node_id_child_at_index() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.child_at_index(node, 0)


def test_invalid_node_id_new_with_children() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.new_with_children(waxy.Style(), [node])


def test_invalid_node_id_print_tree() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.print_tree(node)


def test_invalid_node_id_compute_layout() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.InvalidNodeId):
        tree.compute_layout(node)


def test_invalid_node_id_catchable_as_key_error() -> None:
    tree, node = _removed_node()
    with pytest.raises(KeyError):
        tree.children(node)


def test_invalid_node_id_catchable_as_taffy_exception() -> None:
    tree, node = _removed_node()
    with pytest.raises(waxy.TaffyException):
        tree.children(node)


def test_invalid_node_id_catchable_as_exception() -> None:
    tree, node = _removed_node()
    with pytest.raises(Exception, match="not present in the tree"):
        tree.children(node)


def test_measure_error_preserved_over_invalid_node_id() -> None:
    """A Python exception from the measure function takes priority over InvalidNodeId."""
    tree = waxy.TaffyTree[str]()
    node = tree.new_leaf_with_context(waxy.Style(), "ctx")
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def bad_measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: str,
    ) -> waxy.Size:
        msg = "measure callback failed"
        raise TypeError(msg)

    # The Python exception from the measure callback must propagate as-is,
    # not be swallowed and converted to InvalidNodeId.
    with pytest.raises(TypeError, match="measure callback failed"):
        tree.compute_layout(root, measure=bad_measure)
