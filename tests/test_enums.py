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


def test_available_space_types() -> None:
    assert isinstance(waxy.Definite(100.0), waxy.Definite)
    assert isinstance(waxy.MinContent(), waxy.MinContent)
    assert isinstance(waxy.MaxContent(), waxy.MaxContent)


def test_definite_is_not_min_or_max_content() -> None:
    d = waxy.Definite(100.0)
    assert not isinstance(d, waxy.MinContent)
    assert not isinstance(d, waxy.MaxContent)


def test_enum_equality() -> None:
    assert waxy.Display.Flex == waxy.Display.Flex
    assert waxy.Display.Flex != waxy.Display.Grid
