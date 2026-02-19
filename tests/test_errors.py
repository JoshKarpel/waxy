import pytest

import waxy

TAFFY_EXCEPTION_SUBCLASSES = [
    waxy.ChildIndexOutOfBounds,
    waxy.InvalidParentNode,
    waxy.InvalidChildNode,
    waxy.InvalidInputNode,
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
