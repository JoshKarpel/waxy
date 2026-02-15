import wax


def test_size_default():
    s = wax.Size()
    assert s.width == 0.0
    assert s.height == 0.0


def test_size_values():
    s = wax.Size(10.0, 20.0)
    assert s.width == 10.0
    assert s.height == 20.0


def test_size_setters():
    s = wax.Size()
    s.width = 5.0
    s.height = 15.0
    assert s.width == 5.0
    assert s.height == 15.0


def test_size_eq():
    assert wax.Size(1.0, 2.0) == wax.Size(1.0, 2.0)
    assert wax.Size(1.0, 2.0) != wax.Size(3.0, 2.0)


def test_size_repr():
    assert "Size" in repr(wax.Size(1.0, 2.0))


def test_rect_default():
    r = wax.Rect()
    assert r.left == 0.0
    assert r.right == 0.0
    assert r.top == 0.0
    assert r.bottom == 0.0


def test_rect_values():
    r = wax.Rect(1.0, 2.0, 3.0, 4.0)
    assert r.left == 1.0
    assert r.right == 2.0
    assert r.top == 3.0
    assert r.bottom == 4.0


def test_rect_eq():
    assert wax.Rect(1.0, 2.0, 3.0, 4.0) == wax.Rect(1.0, 2.0, 3.0, 4.0)
    assert wax.Rect(1.0, 2.0, 3.0, 4.0) != wax.Rect(0.0, 2.0, 3.0, 4.0)


def test_point_default():
    p = wax.Point()
    assert p.x == 0.0
    assert p.y == 0.0


def test_point_values():
    p = wax.Point(5.0, 10.0)
    assert p.x == 5.0
    assert p.y == 10.0


def test_point_eq():
    assert wax.Point(1.0, 2.0) == wax.Point(1.0, 2.0)


def test_line_default():
    line = wax.Line()
    assert line.start == 0.0
    assert line.end == 0.0


def test_line_values():
    line = wax.Line(1.0, 2.0)
    assert line.start == 1.0
    assert line.end == 2.0
