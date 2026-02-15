import pytest

import waxy


@pytest.mark.parametrize(
    ("factory", "is_auto"),
    [
        (lambda: waxy.Dimension.length(100.0), False),
        (lambda: waxy.Dimension.percent(0.5), False),
        (lambda: waxy.Dimension.auto(), True),
    ],
    ids=["length", "percent", "auto"],
)
def test_dimension_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (lambda: waxy.Dimension.length(10.0), lambda: waxy.Dimension.length(10.0), True),
        (lambda: waxy.Dimension.length(10.0), lambda: waxy.Dimension.length(20.0), False),
        (lambda: waxy.Dimension.auto(), lambda: waxy.Dimension.auto(), True),
        (lambda: waxy.Dimension.auto(), lambda: waxy.Dimension.length(0.0), False),
    ],
    ids=["length_eq", "length_ne", "auto_eq", "auto_ne_length"],
)
def test_dimension_eq(a, b, equal: bool) -> None:  # type: ignore[no-untyped-def]
    assert (a() == b()) == equal


def test_dimension_repr() -> None:
    assert repr(waxy.Dimension.auto())


@pytest.mark.parametrize(
    ("factory", "has_repr"),
    [
        (lambda: waxy.LengthPercentage.length(50.0), True),
        (lambda: waxy.LengthPercentage.percent(0.5), True),
    ],
    ids=["length", "percent"],
)
def test_length_percentage(factory, has_repr: bool) -> None:  # type: ignore[no-untyped-def]
    assert bool(repr(factory())) == has_repr


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (
            lambda: waxy.LengthPercentage.length(10.0),
            lambda: waxy.LengthPercentage.length(10.0),
            True,
        ),
        (
            lambda: waxy.LengthPercentage.length(10.0),
            lambda: waxy.LengthPercentage.percent(10.0),
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
        (lambda: waxy.LengthPercentageAuto.auto(), True),
        (lambda: waxy.LengthPercentageAuto.length(50.0), False),
    ],
    ids=["auto", "length"],
)
def test_length_percentage_auto_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


@pytest.mark.parametrize(
    ("a", "b", "equal"),
    [
        (lambda: waxy.LengthPercentageAuto.auto(), lambda: waxy.LengthPercentageAuto.auto(), True),
        (
            lambda: waxy.LengthPercentageAuto.length(10.0),
            lambda: waxy.LengthPercentageAuto.length(10.0),
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
        (waxy.auto, True),
        (lambda: waxy.length(10.0), False),
        (lambda: waxy.percent(0.5), False),
    ],
    ids=["auto", "length", "percent"],
)
def test_helpers_is_auto(factory, is_auto: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_auto() == is_auto


def test_helpers_zero() -> None:
    assert repr(waxy.zero())
