import pytest

import waxy

ENUM_VARIANTS: list[tuple[type, list[str]]] = [
    (waxy.Display, ["Block", "Flex", "Grid", "Nil", "FlowRoot"]),
    (waxy.Position, ["Static", "Relative", "Absolute", "Fixed", "Sticky"]),
    (waxy.FlexDirection, ["Row", "Column", "RowReverse", "ColumnReverse"]),
    (waxy.FlexWrap, ["NoWrap", "Wrap", "WrapReverse", "Balance", "BalanceReverse"]),
    (
        waxy.AlignItems,
        [
            "Start",
            "End",
            "FlexStart",
            "FlexEnd",
            "Center",
            "Baseline",
            "Stretch",
            "SelfStart",
            "SelfEnd",
            "SafeStart",
            "SafeEnd",
            "SafeFlexStart",
            "SafeFlexEnd",
            "SafeCenter",
            "SafeSelfStart",
            "SafeSelfEnd",
            "Normal",
            "UnsafeStart",
            "UnsafeEnd",
            "UnsafeFlexStart",
            "UnsafeFlexEnd",
            "UnsafeCenter",
            "UnsafeSelfStart",
            "UnsafeSelfEnd",
        ],
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
            "SafeStart",
            "SafeEnd",
            "SafeFlexStart",
            "SafeFlexEnd",
            "SafeCenter",
            "Normal",
            "UnsafeStart",
            "UnsafeEnd",
            "UnsafeFlexStart",
            "UnsafeFlexEnd",
            "UnsafeCenter",
        ],
    ),
    (waxy.Overflow, ["Visible", "Clip", "Hidden", "Scroll"]),
    (waxy.GridAutoFlow, ["Row", "Column", "RowDense", "ColumnDense"]),
    (waxy.BoxSizing, ["BorderBox", "ContentBox"]),
    (waxy.TextAlign, ["Auto", "LegacyLeft", "LegacyRight", "LegacyCenter"]),
    (waxy.Direction, ["Ltr", "Rtl"]),
    (waxy.Float, ["Left", "Right", "Nil"]),
    (waxy.Clear, ["Left", "Right", "Both", "Nil"]),
    (waxy.Contain, ["Nil", "Layout", "Paint", "Content"]),
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


@pytest.mark.parametrize(
    ("enum_class", "variants"),
    ENUM_VARIANTS,
    ids=[cls.__name__ for cls, _ in ENUM_VARIANTS],
)
def test_enum_variants_are_exhaustive(enum_class: type, variants: list[str]) -> None:
    members = {name for name in vars(enum_class) if name[0].isupper()}
    assert members == set(variants)


ENUM_MEMBERS = dict(ENUM_VARIANTS)
ALIGN_ITEMS_FIELDS = ["align_items", "align_self", "justify_items", "justify_self"]


@pytest.mark.parametrize("field", ALIGN_ITEMS_FIELDS)
@pytest.mark.parametrize("member", ENUM_MEMBERS[waxy.AlignItems])
def test_align_items_round_trips_through_style(field: str, member: str) -> None:
    value = getattr(waxy.AlignItems, member)
    assert getattr(waxy.Style(**{field: value}), field) == value


@pytest.mark.parametrize("field", ["align_content", "justify_content"])
@pytest.mark.parametrize("member", ENUM_MEMBERS[waxy.AlignContent])
def test_align_content_round_trips_through_style(field: str, member: str) -> None:
    value = getattr(waxy.AlignContent, member)
    assert getattr(waxy.Style(**{field: value}), field) == value


@pytest.mark.parametrize(
    "other",
    [waxy.AlignItems.SafeCenter, waxy.AlignItems.UnsafeCenter],
)
def test_style_hash_distinguishes_alignment_safety(other: waxy.AlignItems) -> None:
    bare = waxy.Style(align_items=waxy.AlignItems.Center)
    explicit = waxy.Style(align_items=other)
    assert bare != explicit
    assert hash(bare) != hash(explicit)
