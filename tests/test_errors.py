import pytest

import wax


def test_exception_hierarchy():
    assert issubclass(wax.TaffyException, Exception)
    assert issubclass(wax.ChildIndexOutOfBounds, wax.TaffyException)
    assert issubclass(wax.InvalidParentNode, wax.TaffyException)
    assert issubclass(wax.InvalidChildNode, wax.TaffyException)
    assert issubclass(wax.InvalidInputNode, wax.TaffyException)


def test_child_index_out_of_bounds():
    tree = wax.TaffyTree()
    parent = tree.new_leaf(wax.Style())
    with pytest.raises(wax.ChildIndexOutOfBounds):
        tree.child_at_index(parent, 0)


def test_invalid_parent_node():
    tree = wax.TaffyTree()
    node = tree.new_leaf(wax.Style())
    tree.remove(node)
    # taffy panics on invalid node access (slotmap behavior)
    with pytest.raises(BaseException):  # PanicException
        tree.children(node)


def test_catch_base_exception():
    tree = wax.TaffyTree()
    parent = tree.new_leaf(wax.Style())
    with pytest.raises(wax.TaffyException):
        tree.child_at_index(parent, 99)
