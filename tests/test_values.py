"""Tests for the new standalone value types."""

from dataclasses import dataclass

import pytest

import waxy

# --- Length ---


def test_length_construction() -> None:
    length = waxy.Length(100.0)
    assert length.value == 100.0


def test_length_repr() -> None:
    assert repr(waxy.Length(100.0)) == "Length(100)"


def test_length_eq() -> None:
    assert waxy.Length(100.0) == waxy.Length(100.0)
    assert waxy.Length(100.0) != waxy.Length(200.0)
    assert waxy.Length(100.0) != waxy.Percent(0.5)


def test_length_hash() -> None:
    assert hash(waxy.Length(100.0)) == hash(waxy.Length(100.0))
    s = {waxy.Length(1.0), waxy.Length(2.0), waxy.Length(1.0)}
    assert len(s) == 2


def test_length_match_positional() -> None:
    match waxy.Length(42.0):
        case waxy.Length(v):
            assert v == 42.0
        case _:
            pytest.fail("pattern match failed")


def test_length_match_args() -> None:
    assert waxy.Length.__match_args__ == ("value",)


# --- Percent ---


def test_percent_construction() -> None:
    p = waxy.Percent(0.5)
    assert p.value == 0.5


def test_percent_boundary_valid() -> None:
    assert waxy.Percent(0.0).value == 0.0
    assert waxy.Percent(1.0).value == 1.0


def test_percent_invalid_above_raises() -> None:
    with pytest.raises(waxy.InvalidPercent):
        waxy.Percent(1.5)


def test_percent_invalid_below_raises() -> None:
    with pytest.raises(waxy.InvalidPercent):
        waxy.Percent(-0.1)


def test_percent_invalid_is_value_error() -> None:
    with pytest.raises(ValueError, match="must be in"):
        waxy.Percent(2.0)


def test_percent_repr() -> None:
    assert repr(waxy.Percent(0.5)) == "Percent(0.5)"


def test_percent_eq() -> None:
    assert waxy.Percent(0.5) == waxy.Percent(0.5)
    assert waxy.Percent(0.5) != waxy.Percent(0.75)
    assert waxy.Percent(0.5) != waxy.Length(0.5)


def test_percent_hash() -> None:
    assert hash(waxy.Percent(0.5)) == hash(waxy.Percent(0.5))


def test_percent_match() -> None:
    match waxy.Percent(0.25):
        case waxy.Percent(v):
            assert v == 0.25
        case _:
            pytest.fail("pattern match failed")


# --- Auto ---


def test_auto_construction() -> None:
    a = waxy.Auto()
    assert isinstance(a, waxy.Auto)


def test_auto_repr() -> None:
    assert repr(waxy.Auto()) == "Auto()"


def test_auto_eq() -> None:
    assert waxy.Auto() == waxy.Auto()
    assert waxy.Auto() != waxy.Length(0.0)


def test_auto_hash() -> None:
    assert hash(waxy.Auto()) == hash(waxy.Auto())


def test_auto_constant_is_auto() -> None:
    assert isinstance(waxy.AUTO, waxy.Auto)
    assert waxy.Auto() == waxy.AUTO


# --- MinContent ---


def test_min_content_construction() -> None:
    mc = waxy.MinContent()
    assert isinstance(mc, waxy.MinContent)


def test_min_content_repr() -> None:
    assert repr(waxy.MinContent()) == "MinContent()"


def test_min_content_eq() -> None:
    assert waxy.MinContent() == waxy.MinContent()
    assert waxy.MinContent() != waxy.MaxContent()


def test_min_content_constant() -> None:
    assert isinstance(waxy.MIN_CONTENT, waxy.MinContent)
    assert waxy.MinContent() == waxy.MIN_CONTENT


# --- MaxContent ---


def test_max_content_construction() -> None:
    mc = waxy.MaxContent()
    assert isinstance(mc, waxy.MaxContent)


def test_max_content_repr() -> None:
    assert repr(waxy.MaxContent()) == "MaxContent()"


def test_max_content_eq() -> None:
    assert waxy.MaxContent() == waxy.MaxContent()
    assert waxy.MaxContent() != waxy.MinContent()


def test_max_content_constant() -> None:
    assert isinstance(waxy.MAX_CONTENT, waxy.MaxContent)
    assert waxy.MaxContent() == waxy.MAX_CONTENT


# --- Definite ---


def test_definite_construction() -> None:
    d = waxy.Definite(100.0)
    assert d.value == 100.0


def test_definite_repr() -> None:
    assert repr(waxy.Definite(50.0)) == "Definite(50)"


def test_definite_eq() -> None:
    assert waxy.Definite(100.0) == waxy.Definite(100.0)
    assert waxy.Definite(100.0) != waxy.Definite(200.0)


def test_definite_match() -> None:
    match waxy.Definite(50.0):
        case waxy.Definite(v):
            assert v == 50.0
        case _:
            pytest.fail("pattern match failed")


# --- Fraction ---


def test_fraction_construction() -> None:
    f = waxy.Fraction(1.0)
    assert f.value == 1.0


def test_fraction_repr() -> None:
    assert repr(waxy.Fraction(2.0)) == "Fraction(2)"


def test_fraction_eq() -> None:
    assert waxy.Fraction(1.0) == waxy.Fraction(1.0)
    assert waxy.Fraction(1.0) != waxy.Fraction(2.0)


def test_fraction_match() -> None:
    match waxy.Fraction(2.5):
        case waxy.Fraction(v):
            assert v == 2.5
        case _:
            pytest.fail("pattern match failed")


# --- FitContent ---


def test_fit_content_with_length() -> None:
    fc = waxy.FitContent(waxy.Length(100.0))
    assert fc.limit == waxy.Length(100.0)


def test_fit_content_with_percent() -> None:
    fc = waxy.FitContent(waxy.Percent(0.5))
    assert fc.limit == waxy.Percent(0.5)


def test_fit_content_repr() -> None:
    fc = waxy.FitContent(waxy.Length(100.0))
    assert "FitContent" in repr(fc)
    assert "Length" in repr(fc)


def test_fit_content_eq() -> None:
    assert waxy.FitContent(waxy.Length(100.0)) == waxy.FitContent(waxy.Length(100.0))
    assert waxy.FitContent(waxy.Length(100.0)) != waxy.FitContent(waxy.Length(200.0))


def test_fit_content_hash() -> None:
    assert hash(waxy.FitContent(waxy.Length(100.0))) == hash(waxy.FitContent(waxy.Length(100.0)))


def test_fit_content_match() -> None:
    match waxy.FitContent(waxy.Length(100.0)):
        case waxy.FitContent(limit):
            assert limit == waxy.Length(100.0)
        case _:
            pytest.fail("pattern match failed")


# --- Minmax ---


def test_minmax_construction() -> None:
    mm = waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0))
    assert isinstance(mm.min, waxy.Auto)
    assert mm.max == waxy.Fraction(1.0)


def test_minmax_with_length_min() -> None:
    mm = waxy.Minmax(waxy.Length(100.0), waxy.Fraction(1.0))
    assert mm.min == waxy.Length(100.0)
    assert mm.max == waxy.Fraction(1.0)


def test_minmax_repr() -> None:
    mm = waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0))
    assert "Minmax" in repr(mm)


def test_minmax_eq() -> None:
    assert waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0)) == waxy.Minmax(
        waxy.Auto(), waxy.Fraction(1.0)
    )
    assert waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0)) != waxy.Minmax(
        waxy.Auto(), waxy.Fraction(2.0)
    )


def test_minmax_hash() -> None:
    assert hash(waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0))) == hash(
        waxy.Minmax(waxy.Auto(), waxy.Fraction(1.0))
    )


def test_minmax_match() -> None:
    match waxy.Minmax(waxy.Length(100.0), waxy.Fraction(1.0)):
        case waxy.Minmax(min_val, max_val):
            assert min_val == waxy.Length(100.0)
            assert max_val == waxy.Fraction(1.0)
        case _:
            pytest.fail("pattern match failed")


# --- GridLine ---


def test_grid_line_positive() -> None:
    gl = waxy.GridLine(1)
    assert gl.index == 1


def test_grid_line_negative() -> None:
    gl = waxy.GridLine(-1)
    assert gl.index == -1


def test_grid_line_repr() -> None:
    assert repr(waxy.GridLine(2)) == "GridLine(2)"


def test_grid_line_eq() -> None:
    assert waxy.GridLine(1) == waxy.GridLine(1)
    assert waxy.GridLine(1) != waxy.GridLine(2)
    assert waxy.GridLine(1) != waxy.GridSpan(1)


def test_grid_line_hash() -> None:
    assert hash(waxy.GridLine(1)) == hash(waxy.GridLine(1))


def test_grid_line_match() -> None:
    match waxy.GridLine(2):
        case waxy.GridLine(n):
            assert n == 2
        case _:
            pytest.fail("pattern match failed")


# --- GridSpan ---


def test_grid_span_construction() -> None:
    gs = waxy.GridSpan(3)
    assert gs.count == 3


def test_grid_span_repr() -> None:
    assert repr(waxy.GridSpan(3)) == "GridSpan(3)"


def test_grid_span_eq() -> None:
    assert waxy.GridSpan(2) == waxy.GridSpan(2)
    assert waxy.GridSpan(2) != waxy.GridSpan(3)


def test_grid_span_hash() -> None:
    assert hash(waxy.GridSpan(2)) == hash(waxy.GridSpan(2))


def test_grid_span_match() -> None:
    match waxy.GridSpan(4):
        case waxy.GridSpan(n):
            assert n == 4
        case _:
            pytest.fail("pattern match failed")


# --- GridPlacement with new value types ---


def test_grid_placement_defaults_to_auto() -> None:
    gp = waxy.GridPlacement()
    assert isinstance(gp.start, waxy.Auto)
    assert isinstance(gp.end, waxy.Auto)


def test_grid_placement_line_and_span() -> None:
    gp = waxy.GridPlacement(start=waxy.GridLine(1), end=waxy.GridSpan(3))
    match gp.start:
        case waxy.GridLine(n):
            assert n == 1
        case _:
            pytest.fail("expected GridLine")
    match gp.end:
        case waxy.GridSpan(n):
            assert n == 3
        case _:
            pytest.fail("expected GridSpan")


def test_grid_placement_auto_start() -> None:
    gp = waxy.GridPlacement(start=waxy.Auto(), end=waxy.GridLine(2))
    assert isinstance(gp.start, waxy.Auto)
    assert gp.end == waxy.GridLine(2)


def test_grid_placement_repr() -> None:
    gp = waxy.GridPlacement(start=waxy.GridLine(1), end=waxy.GridSpan(2))
    assert "GridPlacement" in repr(gp)


# --- Style construction with new types ---


def test_style_dimension_fields() -> None:
    s = waxy.Style(size_width=waxy.Length(100.0), size_height=waxy.Percent(0.5))
    assert s.size_width == waxy.Length(100.0)
    assert s.size_height == waxy.Percent(0.5)


def test_style_auto_dimension() -> None:
    s = waxy.Style(size_width=waxy.AUTO)
    assert s.size_width == waxy.Auto()


def test_style_padding_length_percent() -> None:
    s = waxy.Style(padding_left=waxy.Length(10.0), padding_right=waxy.Percent(0.1))
    assert s.padding_left == waxy.Length(10.0)
    assert s.padding_right == waxy.Percent(0.1)


def test_style_margin_auto() -> None:
    s = waxy.Style(margin_left=waxy.Length(10.0), margin_right=waxy.AUTO)
    assert s.margin_left == waxy.Length(10.0)
    assert isinstance(s.margin_right, waxy.Auto)


def test_style_grid_tracks_roundtrip() -> None:
    """Grid tracks should round-trip through shorthand recognition."""
    s = waxy.Style(
        display=waxy.Display.Grid,
        grid_template_columns=[
            waxy.Length(100.0),
            waxy.Fraction(1.0),
            waxy.AUTO,
            waxy.MinContent(),
            waxy.MaxContent(),
        ],
    )
    cols = s.grid_template_columns
    assert cols[0] == waxy.Length(100.0)
    assert cols[1] == waxy.Fraction(1.0)
    assert cols[2] == waxy.Auto()
    assert cols[3] == waxy.MinContent()
    assert cols[4] == waxy.MaxContent()


def test_style_grid_track_minmax_roundtrip() -> None:
    s = waxy.Style(
        grid_template_rows=[
            waxy.Minmax(waxy.Length(50.0), waxy.Fraction(1.0)),
            waxy.FitContent(waxy.Length(200.0)),
        ]
    )
    rows = s.grid_template_rows
    assert isinstance(rows[0], waxy.Minmax)
    assert rows[0].min == waxy.Length(50.0)
    assert rows[0].max == waxy.Fraction(1.0)
    assert isinstance(rows[1], waxy.FitContent)
    assert rows[1].limit == waxy.Length(200.0)


def test_style_grid_placement_pattern_match() -> None:
    s = waxy.Style(
        grid_row=waxy.GridPlacement(start=waxy.GridLine(1), end=waxy.GridSpan(2)),
        grid_column=waxy.GridPlacement(start=waxy.GridLine(2), end=waxy.GridLine(4)),
    )
    match s.grid_row.start:
        case waxy.GridLine(n):
            assert n == 1
        case _:
            pytest.fail("expected GridLine")
    match s.grid_row.end:
        case waxy.GridSpan(n):
            assert n == 2
        case _:
            pytest.fail("expected GridSpan")
    match s.grid_column.end:
        case waxy.GridLine(n):
            assert n == 4
        case _:
            pytest.fail("expected GridLine")


# --- AvailableSize ---


def test_available_size_construction() -> None:
    avail = waxy.AvailableSize(width=waxy.Definite(800.0), height=waxy.MaxContent())
    assert isinstance(avail.width, waxy.Definite)
    assert avail.width.value == 800.0
    assert isinstance(avail.height, waxy.MaxContent)


def test_available_size_min_content() -> None:
    avail = waxy.AvailableSize(width=waxy.MinContent(), height=waxy.MinContent())
    assert isinstance(avail.width, waxy.MinContent)
    assert isinstance(avail.height, waxy.MinContent)


def test_available_size_unpack() -> None:
    avail = waxy.AvailableSize(width=waxy.Definite(100.0), height=waxy.MinContent())
    w, h = avail
    assert isinstance(w, waxy.Definite)
    assert w.value == 100.0
    assert isinstance(h, waxy.MinContent)


def test_available_size_repr() -> None:
    avail = waxy.AvailableSize(width=waxy.Definite(100.0), height=waxy.MaxContent())
    assert "AvailableSize" in repr(avail)
    assert "100" in repr(avail)


def test_available_size_eq() -> None:
    a = waxy.AvailableSize(width=waxy.Definite(100.0), height=waxy.MaxContent())
    b = waxy.AvailableSize(width=waxy.Definite(100.0), height=waxy.MaxContent())
    assert a == b


def test_available_size_pattern_match() -> None:
    avail = waxy.AvailableSize(width=waxy.Definite(50.0), height=waxy.MaxContent())
    match avail.width:
        case waxy.Definite(v):
            assert v == 50.0
        case _:
            pytest.fail("expected Definite")
    match avail.height:
        case waxy.MaxContent():
            pass
        case _:
            pytest.fail("expected MaxContent")


# --- Measure function using pattern matching ---


@dataclass(frozen=True, slots=True)
class FixedContent:
    width: float
    height: float


def test_measure_with_available_size_pattern_match() -> None:
    """Measure function can use pattern matching on AvailableSize."""
    tree = waxy.TaffyTree[FixedContent]()
    node = tree.new_leaf_with_context(waxy.Style(), FixedContent(width=80.0, height=40.0))
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def measure(
        known_dimensions: waxy.KnownSize,
        available_space: waxy.AvailableSize,
        context: FixedContent,
    ) -> waxy.Size:
        kw, kh = known_dimensions
        return waxy.Size(
            kw if kw is not None else context.width,
            kh if kh is not None else context.height,
        )

    tree.compute_layout(root, measure=measure)
    layout = tree.layout(node)
    assert layout.size.width == 80.0
    assert layout.size.height == 40.0
