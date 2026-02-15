import pytest

import wax


@pytest.mark.parametrize(
    ("factory", "is_auto"),
    [
        (lambda: wax.Dimension.length(100.0), False),
        (lambda: wax.Dimension.percent(0.5), False),
        (lambda: wax.Dimension.auto(), True),
    ],
    ids=["length", "percent", "auto"],
)
def test_dimension_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (lambda: wax.Dimension.length(10.0), lambda: wax.Dimension.length(10.0), True),
        (lambda: wax.Dimension.length(10.0), lambda: wax.Dimension.length(20.0), False),
        (lambda: wax.Dimension.auto(), lambda: wax.Dimension.auto(), True),
        (lambda: wax.Dimension.auto(), lambda: wax.Dimension.length(0.0), False),
    ],
    ids=["length_eq", "length_ne", "auto_eq", "auto_ne_length"],
)
def test_dimension_eq(a, b, equal: bool) -> None:  # type: ignore[no-untyped-def]
    assert (a() == b()) == equal


def test_dimension_repr() -> None:
    assert repr(wax.Dimension.auto())


@pytest.mark.parametrize(
    ("factory", "has_repr"),
    [
        (lambda: wax.LengthPercentage.length(50.0), True),
        (lambda: wax.LengthPercentage.percent(0.5), True),
    ],
    ids=["length", "percent"],
)
def test_length_percentage(factory, has_repr: bool) -> None:  # type: ignore[no-untyped-def]
    assert bool(repr(factory())) == has_repr


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (
            lambda: wax.LengthPercentage.length(10.0),
            lambda: wax.LengthPercentage.length(10.0),
            True,
        ),
        (
            lambda: wax.LengthPercentage.length(10.0),
            lambda: wax.LengthPercentage.percent(10.0),
            False,
        ),
    ],
    ids=["length_eq", "length_ne_percent"],
)
def test_length_percentage_eq(a, b, equal: bool) -> None:  # type: ignore[no-untyped-def]
    assert (a() == b()) == equal


@pytest.mark.parametrize(
    ("factory", "is_auto"),
    [
        (lambda: wax.LengthPercentageAuto.auto(), True),
        (lambda: wax.LengthPercentageAuto.length(50.0), False),
    ],
    ids=["auto", "length"],
)
def test_length_percentage_auto_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (lambda: wax.LengthPercentageAuto.auto(), lambda: wax.LengthPercentageAuto.auto(), True),
        (
            lambda: wax.LengthPercentageAuto.length(10.0),
            lambda: wax.LengthPercentageAuto.length(10.0),
            True,
        ),
    ],
    ids=["auto_eq", "length_eq"],
)
def test_length_percentage_auto_eq(a, b, equal: bool) -> None:  # type: ignore[no-untyped-def]
    assert (a() == b()) == equal


@pytest.mark.parametrize(
    ("factory", "is_auto"),
    [
        (wax.auto, True),
        (lambda: wax.length(10.0), False),
        (lambda: wax.percent(0.5), False),
    ],
    ids=["auto", "length", "percent"],
)
def test_helpers_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


def test_helpers_zero() -> None:
    assert repr(wax.zero())
