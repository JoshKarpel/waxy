import pytest

import waxy

GEOMETRY_TYPES: list[tuple[type, list[str], list[float]]] = [
    (waxy.Size, ["width", "height"], [10.0, 20.0]),
    (waxy.Rect, ["left", "right", "top", "bottom"], [1.0, 2.0, 3.0, 4.0]),
    (waxy.Point, ["x", "y"], [5.0, 10.0]),
    (waxy.Line, ["start", "end"], [1.0, 2.0]),
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


def test_size_immutable() -> None:
    s = waxy.Size()
    with pytest.raises(AttributeError):
        setattr(s, "width", 5.0)


def test_point_add() -> None:
    p = waxy.Point(1.0, 2.0) + waxy.Point(3.0, 4.0)
    assert p == waxy.Point(4.0, 6.0)


def test_point_sub() -> None:
    p = waxy.Point(5.0, 10.0) - waxy.Point(3.0, 4.0)
    assert p == waxy.Point(2.0, 6.0)


def test_rect_contains() -> None:
    r = waxy.Rect(0.0, 10.0, 0.0, 10.0)
    assert r.contains(waxy.Point(5.0, 5.0))
    assert r.contains(waxy.Point(0.0, 0.0))  # edge
    assert r.contains(waxy.Point(10.0, 10.0))  # edge
    assert not r.contains(waxy.Point(-1.0, 5.0))
    assert not r.contains(waxy.Point(5.0, 11.0))


def test_rect_corner_properties() -> None:
    r = waxy.Rect(1.0, 3.0, 2.0, 4.0)
    assert r.top_left == waxy.Point(1.0, 2.0)
    assert r.top_right == waxy.Point(3.0, 2.0)
    assert r.bottom_right == waxy.Point(3.0, 4.0)
    assert r.bottom_left == waxy.Point(1.0, 4.0)


def test_rect_top_edge() -> None:
    r = waxy.Rect(0.0, 3.0, 0.0, 2.0)
    assert list(r.top_edge()) == [
        waxy.Point(0.0, 0.0),
        waxy.Point(1.0, 0.0),
        waxy.Point(2.0, 0.0),
        waxy.Point(3.0, 0.0),
    ]


def test_rect_bottom_edge() -> None:
    r = waxy.Rect(0.0, 3.0, 0.0, 2.0)
    assert list(r.bottom_edge()) == [
        waxy.Point(0.0, 2.0),
        waxy.Point(1.0, 2.0),
        waxy.Point(2.0, 2.0),
        waxy.Point(3.0, 2.0),
    ]


def test_rect_left_edge() -> None:
    r = waxy.Rect(0.0, 3.0, 0.0, 2.0)
    assert list(r.left_edge()) == [
        waxy.Point(0.0, 0.0),
        waxy.Point(0.0, 1.0),
        waxy.Point(0.0, 2.0),
    ]


def test_rect_right_edge() -> None:
    r = waxy.Rect(0.0, 3.0, 0.0, 2.0)
    assert list(r.right_edge()) == [
        waxy.Point(3.0, 0.0),
        waxy.Point(3.0, 1.0),
        waxy.Point(3.0, 2.0),
    ]


def test_rect_edge_fractional() -> None:
    r = waxy.Rect(0.5, 2.5, 0.5, 2.5)
    assert list(r.top_edge()) == [waxy.Point(1.0, 1.0), waxy.Point(2.0, 1.0)]
    assert list(r.left_edge()) == [waxy.Point(1.0, 1.0), waxy.Point(1.0, 2.0)]


def test_rect_corners() -> None:
    r = waxy.Rect(1.0, 3.0, 2.0, 4.0)
    corners = r.corners()
    assert corners == (
        waxy.Point(1.0, 2.0),
        waxy.Point(3.0, 2.0),
        waxy.Point(3.0, 4.0),
        waxy.Point(1.0, 4.0),
    )
    assert len(corners) == 4


def test_rect_iter_integer_pixels() -> None:
    r = waxy.Rect(0.0, 2.0, 0.0, 1.0)
    points = list(r)
    assert points == [
        waxy.Point(0.0, 0.0),
        waxy.Point(1.0, 0.0),
        waxy.Point(2.0, 0.0),
        waxy.Point(0.0, 1.0),
        waxy.Point(1.0, 1.0),
        waxy.Point(2.0, 1.0),
    ]


def test_rect_iter_fractional_edges() -> None:
    r = waxy.Rect(0.5, 2.5, 0.5, 1.5)
    points = list(r)
    assert points == [
        waxy.Point(1.0, 1.0),
        waxy.Point(2.0, 1.0),
    ]


def test_rect_len() -> None:
    assert len(waxy.Rect(0.0, 2.0, 0.0, 1.0)) == 6
    assert len(waxy.Rect(0.5, 2.5, 0.5, 1.5)) == 2


def test_rect_len_empty() -> None:
    assert len(waxy.Rect(0.5, 0.6, 0.0, 1.0)) == 0


def test_line_iter() -> None:
    line = waxy.Line(0.0, 3.0)
    assert list(line) == [0.0, 1.0, 2.0, 3.0]


def test_line_iter_fractional() -> None:
    line = waxy.Line(0.5, 2.5)
    assert list(line) == [1.0, 2.0]


def test_line_len() -> None:
    assert len(waxy.Line(0.0, 3.0)) == 4
    assert len(waxy.Line(0.5, 2.5)) == 2
    assert len(waxy.Line(0.5, 0.6)) == 0


def test_size_repr() -> None:
    assert "Size" in repr(waxy.Size(1.0, 2.0))
