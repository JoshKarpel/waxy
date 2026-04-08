from collections.abc import Iterator
from typing import Protocol

import pytest

import waxy


class _EnumLike(Protocol):
    __name__: str

    def __iter__(self) -> Iterator[object]: ...


ENUM_VARIANTS: list[tuple[_EnumLike, list[str]]] = [
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
        [
            "Start",
            "End",
            "FlexStart",
            "FlexEnd",
            "Center",
            "Stretch",
            "SpaceBetween",
            "SpaceEvenly",
            "SpaceAround",
        ],
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
def test_enum_variants(enum_class: _EnumLike, variants: list[str]) -> None:
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
    assert waxy.Display.Flex != waxy.Display.Grid  # type: ignore[comparison-overlap]


@pytest.mark.parametrize(
    ("enum_class", "variants"),
    ENUM_VARIANTS,
    ids=[cls.__name__ for cls, _ in ENUM_VARIANTS],
)
def test_enum_iterable(enum_class: _EnumLike, variants: list[str]) -> None:
    result = list(enum_class)
    assert len(result) == len(variants)
    for variant, name in zip(result, variants, strict=True):
        assert variant == getattr(enum_class, name)
