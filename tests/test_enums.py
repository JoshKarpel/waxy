from collections.abc import Callable

import pytest

import waxy

ENUM_VARIANTS: list[tuple[type, list[str]]] = [
    (waxy.Display, ["Block", "Flex", "Grid", "Nil"]),
    (waxy.Position, ["Relative", "Absolute"]),
    (waxy.FlexDirection, ["Row", "Column", "RowReverse", "ColumnReverse"]),
    (waxy.FlexWrap, ["NoWrap", "Wrap", "WrapReverse"]),
    (
        waxy.AlignItems,
        ["Start", "End", "FlexStart", "FlexEnd", "Center", "Baseline", "Stretch"],
    ),
    (
        waxy.AlignContent,
        ["Start", "End", "Center", "Stretch", "SpaceBetween", "SpaceEvenly", "SpaceAround"],
    ),
    (waxy.Overflow, ["Visible", "Clip", "Hidden", "Scroll"]),
    (waxy.GridAutoFlow, ["Row", "Column", "RowDense", "ColumnDense"]),
    (waxy.BoxSizing, ["BorderBox", "ContentBox"]),
    (waxy.TextAlign, ["Auto", "LegacyLeft", "LegacyRight", "LegacyCenter"]),
]


@pytest.mark.parametrize(
    ("enum_class", "variants"),
    ENUM_VARIANTS,
    ids=[cls.__name__ for cls, _ in ENUM_VARIANTS],
)
def test_enum_variants(enum_class: type, variants: list[str]) -> None:
    for name in variants:
        assert getattr(enum_class, name) is not None


@pytest.mark.parametrize(
    ("factory", "is_definite"),
    [
        (lambda: waxy.AvailableSpace.definite(100.0), True),
        (lambda: waxy.AvailableSpace.min_content(), False),
        (lambda: waxy.AvailableSpace.max_content(), False),
    ],
    ids=["definite", "min_content", "max_content"],
)
def test_available_space(factory: Callable[[], waxy.AvailableSpace], is_definite: bool) -> None:
    assert factory().is_definite() == is_definite


def test_enum_equality() -> None:
    assert waxy.Display.Flex == waxy.Display.Flex
    assert waxy.Display.Flex != waxy.Display.Grid
