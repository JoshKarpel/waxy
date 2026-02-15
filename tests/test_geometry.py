import pytest

import wax

GEOMETRY_TYPES: list[tuple[type, list[str], list[float]]] = [
    (wax.Size, ["width", "height"], [10.0, 20.0]),
    (wax.Rect, ["left", "right", "top", "bottom"], [1.0, 2.0, 3.0, 4.0]),
    (wax.Point, ["x", "y"], [5.0, 10.0]),
    (wax.Line, ["start", "end"], [1.0, 2.0]),
]


@pytest.mark.parametrize(
    ("cls", "attrs", "_values"),
    GEOMETRY_TYPES,
    ids=[cls.__name__ for cls, _, _ in GEOMETRY_TYPES],
)
def test_geometry_default(cls: type, attrs: list[str], _values: list[float]) -> None:
    obj = cls()
    for attr in attrs:
        assert getattr(obj, attr) == 0.0


@pytest.mark.parametrize(
    ("cls", "attrs", "values"),
    GEOMETRY_TYPES,
    ids=[cls.__name__ for cls, _, _ in GEOMETRY_TYPES],
)
def test_geometry_values(cls: type, attrs: list[str], values: list[float]) -> None:
    obj = cls(*values)
    for attr, val in zip(attrs, values):
        assert getattr(obj, attr) == val


@pytest.mark.parametrize(
    ("cls", "attrs", "values"),
    GEOMETRY_TYPES[:2],
    ids=[cls.__name__ for cls, _, _ in GEOMETRY_TYPES[:2]],
)
def test_geometry_eq(cls: type, attrs: list[str], values: list[float]) -> None:
    assert cls(*values) == cls(*values)
    modified = [v + 1.0 for v in values]
    assert cls(*values) != cls(*modified)


def test_size_setters() -> None:
    s = wax.Size()
    s.width = 5.0
    s.height = 15.0
    assert s.width == 5.0
    assert s.height == 15.0


def test_size_repr() -> None:
    assert "Size" in repr(wax.Size(1.0, 2.0))
