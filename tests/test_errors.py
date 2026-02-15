import pytest

import wax

EXCEPTION_SUBCLASSES = [
    wax.ChildIndexOutOfBounds,
    wax.InvalidParentNode,
    wax.InvalidChildNode,
    wax.InvalidInputNode,
]


def test_exception_base() -> None:
    assert issubclass(wax.TaffyException, Exception)


@pytest.mark.parametrize(
    "exc_class",
    EXCEPTION_SUBCLASSES,
    ids=[cls.__name__ for cls in EXCEPTION_SUBCLASSES],
)
def test_exception_hierarchy(exc_class: type) -> None:
    assert issubclass(exc_class, wax.TaffyException)


def test_child_index_out_of_bounds() -> None:
    tree = wax.TaffyTree()
    parent = tree.new_leaf(wax.Style())
    with pytest.raises(wax.ChildIndexOutOfBounds):
        tree.child_at_index(parent, 0)


def test_invalid_parent_node() -> None:
    tree = wax.TaffyTree()
    node = tree.new_leaf(wax.Style())
    tree.remove(node)
    # taffy panics on invalid node access (slotmap behavior)
    with pytest.raises(BaseException):  # PanicException
        tree.children(node)


def test_catch_base_exception() -> None:
    tree = wax.TaffyTree()
    parent = tree.new_leaf(wax.Style())
    with pytest.raises(wax.TaffyException):
        tree.child_at_index(parent, 99)
