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
    for attr, val in zip(attrs, values, strict=True):
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
        s.width = 5.0  # type: ignore[misc]


def test_size_hash() -> None:
    assert hash(waxy.Size(10.0, 20.0)) == hash(waxy.Size(10.0, 20.0))
    s = {waxy.Size(1.0, 2.0), waxy.Size(3.0, 4.0), waxy.Size(1.0, 2.0)}
    assert len(s) == 2

    s1 = waxy.Size(0.0, 0.0)
    s2 = waxy.Size(-0.0, 0.0)
    s3 = waxy.Size(0.0, -0.0)
    s4 = waxy.Size(-0.0, -0.0)
    assert s1 == s2 == s3 == s4
    assert hash(s1) == hash(s2) == hash(s3) == hash(s4)
    assert len({s1, s2, s3, s4}) == 1


def test_line_hash() -> None:
    assert hash(waxy.Line(1.0, 2.0)) == hash(waxy.Line(1.0, 2.0))
    s = {waxy.Line(1.0, 2.0), waxy.Line(3.0, 4.0), waxy.Line(1.0, 2.0)}
    assert len(s) == 2

    l1 = waxy.Line(0.0, 0.0)
    l2 = waxy.Line(-0.0, 0.0)
    l3 = waxy.Line(0.0, -0.0)
    l4 = waxy.Line(-0.0, -0.0)
    assert l1 == l2 == l3 == l4
    assert hash(l1) == hash(l2) == hash(l3) == hash(l4)
    assert len({l1, l2, l3, l4}) == 1


def test_point_hash() -> None:
    # Basic hash and deduplication behaviour for non-zero coordinates
    assert hash(waxy.Point(1.0, 2.0)) == hash(waxy.Point(1.0, 2.0))
    s = {waxy.Point(1.0, 2.0), waxy.Point(3.0, 4.0), waxy.Point(1.0, 2.0)}
    assert len(s) == 2

    # Signed zero edge case: 0.0 and -0.0 should be equal and hash-identical
    p1 = waxy.Point(0.0, 0.0)
    p2 = waxy.Point(-0.0, 0.0)
    p3 = waxy.Point(0.0, -0.0)
    p4 = waxy.Point(-0.0, -0.0)
    assert p1 == p2 == p3 == p4
    assert hash(p1) == hash(p2) == hash(p3) == hash(p4)
    assert len({p1, p2, p3, p4}) == 1


def test_point_add() -> None:
    p = waxy.Point(1.0, 2.0) + waxy.Point(3.0, 4.0)
    assert p == waxy.Point(4.0, 6.0)


def test_point_sub() -> None:
    p = waxy.Point(5.0, 10.0) - waxy.Point(3.0, 4.0)
    assert p == waxy.Point(2.0, 6.0)


def test_rect_hash() -> None:
    # Basic hash and deduplication behaviour
    assert hash(waxy.Rect(1.0, 2.0, 3.0, 4.0)) == hash(waxy.Rect(1.0, 2.0, 3.0, 4.0))
    s = {
        waxy.Rect(1.0, 2.0, 3.0, 4.0),
        waxy.Rect(5.0, 6.0, 7.0, 8.0),
        waxy.Rect(1.0, 2.0, 3.0, 4.0),
    }
    assert len(s) == 2

    # Signed zero edge case: 0.0 and -0.0 should be equal and hash-identical
    r1 = waxy.Rect(0.0, 0.0, 0.0, 0.0)
    r2 = waxy.Rect(-0.0, 0.0, 0.0, 0.0)
    r3 = waxy.Rect(0.0, -0.0, 0.0, 0.0)
    r4 = waxy.Rect(-0.0, -0.0, -0.0, -0.0)
    assert r1 == r2 == r3 == r4
    assert hash(r1) == hash(r2) == hash(r3) == hash(r4)
    assert len({r1, r2, r3, r4}) == 1


def test_size_area() -> None:
    assert waxy.Size(3.0, 4.0).area == 12.0
    assert waxy.Size(0.0, 5.0).area == 0.0


def test_point_mul() -> None:
    p = waxy.Point(2.0, 3.0) * 4.0
    assert p == waxy.Point(8.0, 12.0)


def test_point_rmul() -> None:
    p = 4.0 * waxy.Point(2.0, 3.0)
    assert p == waxy.Point(8.0, 12.0)


def test_point_truediv() -> None:
    p = waxy.Point(8.0, 12.0) / 4.0
    assert p == waxy.Point(2.0, 3.0)


def test_point_neg() -> None:
    p = -waxy.Point(2.0, -3.0)
    assert p == waxy.Point(-2.0, 3.0)


def test_size_repr() -> None:
    assert "Size" in repr(waxy.Size(1.0, 2.0))
