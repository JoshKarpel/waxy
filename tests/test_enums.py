import pytest

import wax

ENUM_VARIANTS: list[tuple[type, list[str]]] = [
    (wax.Display, ["Block", "Flex", "Grid", "Nil"]),
    (wax.Position, ["Relative", "Absolute"]),
    (wax.FlexDirection, ["Row", "Column", "RowReverse", "ColumnReverse"]),
    (wax.FlexWrap, ["NoWrap", "Wrap", "WrapReverse"]),
    (
        wax.AlignItems,
        ["Start", "End", "FlexStart", "FlexEnd", "Center", "Baseline", "Stretch"],
    ),
    (
        wax.AlignContent,
        ["Start", "End", "Center", "Stretch", "SpaceBetween", "SpaceEvenly", "SpaceAround"],
    ),
    (wax.Overflow, ["Visible", "Clip", "Hidden", "Scroll"]),
    (wax.GridAutoFlow, ["Row", "Column", "RowDense", "ColumnDense"]),
    (wax.BoxSizing, ["BorderBox", "ContentBox"]),
    (wax.TextAlign, ["Auto", "LegacyLeft", "LegacyRight", "LegacyCenter"]),
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
        (lambda: wax.AvailableSpace.definite(100.0), True),
        (lambda: wax.AvailableSpace.min_content(), False),
        (lambda: wax.AvailableSpace.max_content(), False),
    ],
    ids=["definite", "min_content", "max_content"],
)
def test_available_space(factory, is_definite: bool) -> None:  # type: ignore[no-untyped-def]
    assert factory().is_definite() == is_definite


def test_enum_equality() -> None:
    assert wax.Display.Flex == wax.Display.Flex
    assert wax.Display.Flex != wax.Display.Grid
