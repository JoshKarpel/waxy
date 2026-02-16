import pytest

import waxy

EXCEPTION_SUBCLASSES = [
    waxy.ChildIndexOutOfBounds,
    waxy.InvalidParentNode,
    waxy.InvalidChildNode,
    waxy.InvalidInputNode,
]


def test_exception_base() -> None:
    assert issubclass(waxy.TaffyException, Exception)


@pytest.mark.parametrize(
    "exc_class",
    EXCEPTION_SUBCLASSES,
    ids=[cls.__name__ for cls in EXCEPTION_SUBCLASSES],
)
def test_exception_hierarchy(exc_class: type) -> None:
    assert issubclass(exc_class, waxy.TaffyException)


def test_child_index_out_of_bounds() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.ChildIndexOutOfBounds):
        tree.child_at_index(parent, 0)


def test_invalid_parent_node() -> None:
    tree = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style())
    tree.remove(node)
    # taffy panics on invalid node access (slotmap behavior)
    with pytest.raises(BaseException, match="invalid SlotMap key"):
        tree.children(node)


def test_catch_base_exception() -> None:
    tree = waxy.TaffyTree()
    parent = tree.new_leaf(waxy.Style())
    with pytest.raises(waxy.TaffyException):
        tree.child_at_index(parent, 99)
