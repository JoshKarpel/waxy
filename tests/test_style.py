import inspect
import types
from collections.abc import Callable
from typing import assert_never

import pytest

import waxy


def test_style_default() -> None:
    s = waxy.Style()
    assert s.display == waxy.Display.Flex  # taffy default
    assert s.position == waxy.Position.Relative
    assert s.flex_grow == 0.0
    assert s.flex_shrink == 1.0


def test_style_display() -> None:
    s = waxy.Style(display=waxy.Display.Grid)
    assert s.display == waxy.Display.Grid


def test_style_immutable() -> None:
    s = waxy.Style()
    with pytest.raises(AttributeError):
        s.display = waxy.Display.Block  # type: ignore[misc]


def test_style_flex_properties() -> None:
    s = waxy.Style(
        flex_direction=waxy.FlexDirection.Column,
        flex_wrap=waxy.FlexWrap.Wrap,
        flex_grow=2.0,
        flex_shrink=0.5,
    )
    assert s.flex_direction == waxy.FlexDirection.Column
    assert s.flex_wrap == waxy.FlexWrap.Wrap
    assert s.flex_grow == 2.0
    assert s.flex_shrink == 0.5


def test_style_size() -> None:
    s = waxy.Style(
        size_width=waxy.Length(100.0),
        size_height=waxy.Percent(0.5),
    )
    assert s.size_width == waxy.Length(100.0)
    assert s.size_height == waxy.Percent(0.5)


def test_style_padding() -> None:
    s = waxy.Style(
        padding_left=waxy.Length(10.0),
        padding_right=waxy.Length(10.0),
        padding_top=waxy.Length(5.0),
        padding_bottom=waxy.Length(5.0),
    )
    assert s.padding_left == waxy.Length(10.0)
    assert s.padding_top == waxy.Length(5.0)


def test_style_margin() -> None:
    s = waxy.Style(
        margin_left=waxy.Length(10.0),
        margin_right=waxy.AUTO,
    )
    assert s.margin_left == waxy.Length(10.0)
    assert isinstance(s.margin_right, waxy.Auto)


def test_style_alignment() -> None:
    s = waxy.Style(
        align_items=waxy.AlignItems.Center,
        justify_content=waxy.AlignContent.SpaceBetween,
    )
    assert s.align_items == waxy.AlignItems.Center
    assert s.justify_content == waxy.AlignContent.SpaceBetween


def test_style_alignment_none() -> None:
    s = waxy.Style()
    assert s.align_items is None
    assert s.align_content is None


def test_style_grid() -> None:
    s = waxy.Style(
        display=waxy.Display.Grid,
        grid_template_columns=[
            waxy.Length(100.0),
            waxy.Fraction(1.0),
        ],
    )
    assert s.display == waxy.Display.Grid
    cols = s.grid_template_columns
    assert len(cols) == 2


def test_style_none_uses_default() -> None:
    s = waxy.Style(display=None)
    assert s.display == waxy.Display.Flex  # taffy default


def test_style_or_rhs_overrides_lhs() -> None:
    a = waxy.Style(display=waxy.Display.Flex, flex_grow=1.0)
    b = waxy.Style(display=waxy.Display.Grid)
    result = a | b
    assert result.display == waxy.Display.Grid
    assert result.flex_grow == 1.0  # preserved from a


def test_style_or_unset_fields_not_overridden() -> None:
    a = waxy.Style(flex_grow=2.0, flex_shrink=0.5)
    b = waxy.Style(flex_grow=3.0)
    result = a | b
    assert result.flex_grow == 3.0  # overridden by b
    assert result.flex_shrink == 0.5  # preserved from a


def test_style_or_empty_rhs_preserves_lhs() -> None:
    a = waxy.Style(display=waxy.Display.Block, position=waxy.Position.Absolute)
    b = waxy.Style()
    result = a | b
    assert result.display == waxy.Display.Block
    assert result.position == waxy.Position.Absolute


def test_style_or_chaining() -> None:
    a = waxy.Style(display=waxy.Display.Flex)
    b = waxy.Style(flex_grow=1.0)
    c = waxy.Style(flex_shrink=0.0)
    result = a | b | c
    assert result.display == waxy.Display.Flex
    assert result.flex_grow == 1.0
    assert result.flex_shrink == 0.0


def test_style_or_alignment_fields() -> None:
    a = waxy.Style(align_items=waxy.AlignItems.Center)
    b = waxy.Style(justify_content=waxy.AlignContent.SpaceBetween)
    result = a | b
    assert result.align_items == waxy.AlignItems.Center
    assert result.justify_content == waxy.AlignContent.SpaceBetween


def test_style_or_size_fields() -> None:
    a = waxy.Style(
        size_width=waxy.Length(100.0),
        size_height=waxy.Length(200.0),
    )
    b = waxy.Style(size_width=waxy.Percent(0.5))
    result = a | b
    assert result.size_width == waxy.Percent(0.5)
    assert result.size_height == waxy.Length(200.0)


def test_style_or_does_not_mutate_operands() -> None:
    a = waxy.Style(display=waxy.Display.Flex)
    b = waxy.Style(display=waxy.Display.Grid)
    _ = a | b
    assert a.display == waxy.Display.Flex
    assert b.display == waxy.Display.Grid


def test_style_or_default_value_overrides_when_explicit() -> None:
    """Setting a field to its default value explicitly should still override."""
    a = waxy.Style(flex_grow=2.0)
    b = waxy.Style(flex_grow=0.0)  # 0.0 is the default, but explicitly set
    result = a | b
    assert result.flex_grow == 0.0


def test_style_or_explicit_none_clears_field() -> None:
    """Passing None explicitly should clear the field in the merged result."""
    a = waxy.Style(align_items=waxy.AlignItems.Center)
    b = waxy.Style(align_items=None)
    result = a | b
    assert result.align_items is None


def test_style_or_explicit_none_aspect_ratio() -> None:
    """Passing aspect_ratio=None explicitly should clear it."""
    a = waxy.Style(aspect_ratio=1.5)
    b = waxy.Style(aspect_ratio=None)
    result = a | b
    assert result.aspect_ratio is None


def test_style_or_grid_tracks() -> None:
    a = waxy.Style(
        grid_template_columns=[waxy.Length(100.0)],
    )
    b = waxy.Style(
        grid_template_rows=[waxy.Fraction(1.0)],
    )
    result = a | b
    assert len(result.grid_template_columns) == 1
    assert len(result.grid_template_rows) == 1


def test_style_eq_default() -> None:
    assert waxy.Style() == waxy.Style()


def test_style_eq_same_fields() -> None:
    a = waxy.Style(display=waxy.Display.Grid, flex_grow=2.0)
    b = waxy.Style(display=waxy.Display.Grid, flex_grow=2.0)
    assert a == b


def test_style_eq_different_fields() -> None:
    a = waxy.Style(flex_grow=1.0)
    b = waxy.Style(flex_grow=2.0)
    assert a != b


def test_style_eq_non_style() -> None:
    assert waxy.Style() != "not a style"
    assert waxy.Style() != 42


def test_style_hash() -> None:
    assert hash(waxy.Style()) == hash(waxy.Style())
    a = waxy.Style(display=waxy.Display.Grid, flex_grow=2.0)
    b = waxy.Style(display=waxy.Display.Grid, flex_grow=2.0)
    assert hash(a) == hash(b)
    assert len({a, b, waxy.Style()}) == 2


def test_style_hash_float_normalization() -> None:
    # flex_grow is a plain f32; taffy's derived PartialEq uses IEEE float
    # equality where 0.0 == -0.0, so equal styles must also hash identically.
    a = waxy.Style(flex_grow=0.0)
    b = waxy.Style(flex_grow=-0.0)
    assert a == b
    assert hash(a) == hash(b)


def test_style_hash_grid_tracks() -> None:
    # grid_auto_rows / grid_auto_columns
    a = waxy.Style(grid_auto_rows=[waxy.Length(100.0)], grid_auto_columns=[waxy.Fraction(1.0)])
    b = waxy.Style(grid_auto_rows=[waxy.Length(100.0)], grid_auto_columns=[waxy.Fraction(1.0)])
    assert a == b
    assert hash(a) == hash(b)

    # grid_template_rows / grid_template_columns
    c = waxy.Style(
        grid_template_rows=[waxy.Length(50.0), waxy.Fraction(1.0)],
        grid_template_columns=[waxy.AUTO],
    )
    d = waxy.Style(
        grid_template_rows=[waxy.Length(50.0), waxy.Fraction(1.0)],
        grid_template_columns=[waxy.AUTO],
    )
    assert c == d
    assert hash(c) == hash(d)

    # Different grid tracks hash differently and work as set/dict keys.
    assert len({a, c}) == 2


# Each case: a Style with one new field set, the getter for that field, the value it was
# set to, and the field's default.
NEW_FIELD_CASES: list[tuple[str, waxy.Style, Callable[[waxy.Style], object], object, object]] = [
    (
        "direction",
        waxy.Style(direction=waxy.Direction.Rtl),
        lambda s: s.direction,
        waxy.Direction.Rtl,
        waxy.Direction.Ltr,
    ),
    (
        "contain",
        waxy.Style(contain=waxy.Contain.Paint),
        lambda s: s.contain,
        waxy.Contain.Paint,
        waxy.Contain.Nil,
    ),
    (
        "float",
        waxy.Style(float=waxy.Float.Right),
        lambda s: s.float,
        waxy.Float.Right,
        waxy.Float.Nil,
    ),
    (
        "clear",
        waxy.Style(clear=waxy.Clear.Both),
        lambda s: s.clear,
        waxy.Clear.Both,
        waxy.Clear.Nil,
    ),
    ("item_is_table", waxy.Style(item_is_table=True), lambda s: s.item_is_table, True, False),
    (
        "item_is_replaced",
        waxy.Style(item_is_replaced=True),
        lambda s: s.item_is_replaced,
        True,
        False,
    ),
    ("flex_line_count", waxy.Style(flex_line_count=3), lambda s: s.flex_line_count, 3, 1),
]
NEW_FIELD_IDS = [case[0] for case in NEW_FIELD_CASES]


@pytest.mark.parametrize(
    ("field", "style", "get", "value", "default"), NEW_FIELD_CASES, ids=NEW_FIELD_IDS
)
def test_style_new_field_default(
    field: str,
    style: waxy.Style,
    get: Callable[[waxy.Style], object],
    value: object,
    default: object,
) -> None:
    assert get(waxy.Style()) == default


@pytest.mark.parametrize(
    ("field", "style", "get", "value", "default"), NEW_FIELD_CASES, ids=NEW_FIELD_IDS
)
def test_style_new_field_round_trips(
    field: str,
    style: waxy.Style,
    get: Callable[[waxy.Style], object],
    value: object,
    default: object,
) -> None:
    assert get(style) == value


@pytest.mark.parametrize(
    ("field", "style", "get", "value", "default"), NEW_FIELD_CASES, ids=NEW_FIELD_IDS
)
def test_style_new_field_survives_merge(
    field: str,
    style: waxy.Style,
    get: Callable[[waxy.Style], object],
    value: object,
    default: object,
) -> None:
    assert get(style | waxy.Style(display=waxy.Display.Grid)) == value


@pytest.mark.parametrize(
    ("field", "style", "get", "value", "default"), NEW_FIELD_CASES, ids=NEW_FIELD_IDS
)
def test_style_new_field_affects_eq_and_hash(
    field: str,
    style: waxy.Style,
    get: Callable[[waxy.Style], object],
    value: object,
    default: object,
) -> None:
    assert style != waxy.Style()
    assert hash(style) != hash(waxy.Style())


def test_style_flex_line_count_zero_raises() -> None:
    with pytest.raises(waxy.InvalidFlexLineCount, match="at least 1"):
        waxy.Style(flex_line_count=0)


SIZE_KEYWORDS: list[waxy.DimensionValue] = [
    waxy.MIN_CONTENT,
    waxy.MAX_CONTENT,
    waxy.FIT_CONTENT,
    waxy.STRETCH,
    waxy.FitContent(waxy.Length(120.0)),
    waxy.FitContent(waxy.Percent(0.25)),
]


@pytest.mark.parametrize("value", SIZE_KEYWORDS, ids=repr)
def test_style_size_width_sizing_keywords_round_trip(value: waxy.DimensionValue) -> None:
    assert waxy.Style(size_width=value).size_width == value


@pytest.mark.parametrize("value", SIZE_KEYWORDS, ids=repr)
def test_style_size_height_sizing_keywords_round_trip(value: waxy.DimensionValue) -> None:
    assert waxy.Style(size_height=value).size_height == value


@pytest.mark.parametrize("value", [*SIZE_KEYWORDS, waxy.CONTENT], ids=repr)
def test_style_flex_basis_sizing_keywords_round_trip(value: waxy.FlexBasisValue) -> None:
    assert waxy.Style(flex_basis=value).flex_basis == value


def test_style_size_rejects_content() -> None:
    with pytest.raises(TypeError):
        waxy.Style(size_width=waxy.CONTENT)  # type: ignore[arg-type]


def test_style_min_size_rejects_sizing_keywords() -> None:
    with pytest.raises(TypeError):
        waxy.Style(min_size_width=waxy.STRETCH)  # type: ignore[arg-type]


def test_style_max_size_rejects_sizing_keywords() -> None:
    with pytest.raises(TypeError):
        waxy.Style(max_size_height=waxy.MIN_CONTENT)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [waxy.Length(30.0), waxy.Percent(0.4), waxy.AUTO], ids=repr)
def test_style_min_max_size_round_trip(value: waxy.LengthPercentageAutoValue) -> None:
    style = waxy.Style(
        min_size_width=value, min_size_height=value, max_size_width=value, max_size_height=value
    )
    assert style.min_size_width == value
    assert style.min_size_height == value
    assert style.max_size_width == value
    assert style.max_size_height == value


def test_style_stretch_fills_container_less_margin() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(waxy.Style(size_width=waxy.STRETCH, margin_left=waxy.Length(15.0)))
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Block, size_width=waxy.Length(200.0)), [child]
    )
    tree.compute_layout(root)
    assert tree.layout(child).size.width == 185.0


def test_style_fit_content_limit_clamps_width() -> None:
    # Text that is 50 wide fully wrapped (min-content), 500 wide unwrapped (max-content),
    # and otherwise wraps to the available width.
    def measure(known: waxy.KnownSize, available: waxy.AvailableSize, context: str) -> waxy.Size:
        match available.width:
            case waxy.MinContent():
                width = 50.0
            case waxy.MaxContent():
                width = 500.0
            case waxy.Definite(w):
                width = max(50.0, min(500.0, w))
            case _ as unreachable:
                assert_never(unreachable)
        return waxy.Size(width, 5000.0 / width)

    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    child = tree.new_leaf_with_context(
        waxy.Style(size_width=waxy.FitContent(waxy.Length(120.0))), "text"
    )
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Block, size_width=waxy.Length(300.0)), [child]
    )
    tree.compute_layout(root, measure=measure)
    assert tree.layout(child).size.width == 120.0


# `Style` typed to take any keywords, for building one from a field name chosen at runtime.
style_from_keywords: Callable[..., waxy.Style] = waxy.Style

# Every Style property that is a field, i.e. everything but `fields_set`.
FIELD_NAMES = sorted(
    name
    for name in dir(waxy.Style)
    if isinstance(inspect.getattr_static(waxy.Style, name), types.GetSetDescriptorType)
    and name not in {"__class__", "fields_set"}
)

# A value for every field that differs from its default.
NON_DEFAULT_VALUES: dict[str, object] = {
    "display": waxy.Display.Grid,
    "box_sizing": waxy.BoxSizing.ContentBox,
    "overflow_x": waxy.Overflow.Hidden,
    "overflow_y": waxy.Overflow.Scroll,
    "scrollbar_width": 3.0,
    "position": waxy.Position.Absolute,
    "direction": waxy.Direction.Rtl,
    "contain": waxy.Contain.Layout,
    "float": waxy.Float.Left,
    "clear": waxy.Clear.Both,
    "item_is_table": True,
    "item_is_replaced": True,
    "inset_left": waxy.Length(1),
    "inset_right": waxy.Length(2),
    "inset_top": waxy.Percent(0.25),
    "inset_bottom": waxy.Length(4),
    "size_width": waxy.Length(5),
    "size_height": waxy.STRETCH,
    "min_size_width": waxy.Length(6),
    "min_size_height": waxy.Percent(0.125),
    "max_size_width": waxy.Length(7),
    "max_size_height": waxy.Length(8),
    "aspect_ratio": 1.5,
    "margin_left": waxy.AUTO,
    "margin_right": waxy.Length(9),
    "margin_top": waxy.Percent(0.5),
    "margin_bottom": waxy.Length(10),
    "padding_left": waxy.Length(11),
    "padding_right": waxy.Length(12),
    "padding_top": waxy.Percent(0.375),
    "padding_bottom": waxy.Length(13),
    "border_left": waxy.Length(14),
    "border_right": waxy.Length(15),
    "border_top": waxy.Length(16),
    "border_bottom": waxy.Percent(0.0625),
    "align_items": waxy.AlignItems.Center,
    "align_self": waxy.AlignItems.End,
    "justify_items": waxy.AlignItems.Start,
    "justify_self": waxy.AlignItems.Stretch,
    "align_content": waxy.AlignContent.SpaceBetween,
    "justify_content": waxy.AlignContent.Center,
    "gap_width": waxy.Length(17),
    "gap_height": waxy.Percent(0.75),
    "text_align": waxy.TextAlign.LegacyCenter,
    "flex_direction": waxy.FlexDirection.Column,
    "flex_wrap": waxy.FlexWrap.Wrap,
    "flex_basis": waxy.CONTENT,
    "flex_grow": 2.0,
    "flex_shrink": 0.5,
    "flex_line_count": 3,
    "grid_template_rows": [waxy.Length(18), waxy.Fraction(1)],
    "grid_template_columns": [waxy.Repeat(2, [waxy.AUTO])],
    "grid_template_row_names": [["a"], ["b"], ["c"]],
    "grid_template_column_names": [["x"], ["y"]],
    "grid_template_areas": waxy.GridTemplateAreas.from_strings(["a b"]),
    "grid_auto_rows": [waxy.Length(19)],
    "grid_auto_columns": [waxy.MIN_CONTENT],
    "grid_auto_flow": waxy.GridAutoFlow.Column,
    "grid_row": waxy.GridPlacement(waxy.GridLine(1), waxy.GridSpan(2)),
    "grid_column": waxy.GridPlacement(waxy.NamedGridLine("a")),
}


def test_non_default_values_cover_every_field() -> None:
    assert set(NON_DEFAULT_VALUES) == set(FIELD_NAMES)


@pytest.mark.parametrize("name", FIELD_NAMES)
def test_style_field_with_default_value_is_set(name: str) -> None:
    default = getattr(waxy.Style(), name)
    assert style_from_keywords(**{name: default}).fields_set == {name}


@pytest.mark.parametrize("name", FIELD_NAMES)
def test_style_field_with_non_default_value_round_trips(name: str) -> None:
    value = NON_DEFAULT_VALUES[name]
    assert getattr(style_from_keywords(**{name: value}), name) == value


@pytest.mark.parametrize("name", FIELD_NAMES)
def test_style_field_with_non_default_value_survives_merge(name: str) -> None:
    s = style_from_keywords(**{name: NON_DEFAULT_VALUES[name]})
    assert waxy.Style() | s == s


@pytest.mark.parametrize("name", FIELD_NAMES)
def test_style_field_with_non_default_value_changes_hash(name: str) -> None:
    s = style_from_keywords(**{name: NON_DEFAULT_VALUES[name]})
    assert hash(s) != hash(waxy.Style())


def test_style_unknown_keyword_raises_type_error_naming_it() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'flex_grw'"):
        waxy.Style(flex_grw=1)  # type: ignore[call-arg]


def test_style_unknown_keyword_with_none_raises() -> None:
    with pytest.raises(TypeError, match="unexpected keyword argument 'flex_grw'"):
        waxy.Style(flex_grw=None)  # type: ignore[call-arg]


def test_style_wrong_value_type_notes_the_keyword() -> None:
    with pytest.raises(TypeError) as excinfo:
        waxy.Style(size_width=1)  # type: ignore[arg-type]
    assert excinfo.value.__notes__ == ["while processing 'size_width'"]


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (waxy.Style(), waxy.Style(flex_grow=0)),
        (waxy.Style(), waxy.Style(display=waxy.Display.Flex)),
        (waxy.Style(), waxy.Style(align_items=None)),
        (waxy.Style(flex_grow=3) | waxy.Style(), waxy.Style(flex_grow=3) | waxy.Style(flex_grow=0)),
    ],
)
def test_style_same_values_different_set_fields_are_unequal(a: waxy.Style, b: waxy.Style) -> None:
    assert a != b


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (waxy.Style(flex_grow=1), waxy.Style(flex_grow=1.0)),
        (waxy.Style(size_width=waxy.AUTO), waxy.Style(size_width=waxy.Auto())),
        (waxy.Style(align_items=None), waxy.Style(align_items=None)),
    ],
)
def test_style_same_values_same_set_fields_are_equal_and_hash_equal(
    a: waxy.Style, b: waxy.Style
) -> None:
    assert a == b
    assert hash(a) == hash(b)


@pytest.mark.parametrize(
    ("merged", "direct"),
    [
        (waxy.Style(flex_grow=3) | waxy.Style(flex_grow=0), waxy.Style(flex_grow=0)),
        (
            waxy.Style(flex_grow=3) | waxy.Style(flex_shrink=2),
            waxy.Style(flex_grow=3, flex_shrink=2),
        ),
        (
            waxy.Style(align_items=waxy.AlignItems.Center) | waxy.Style(align_items=None),
            waxy.Style(align_items=None),
        ),
    ],
)
def test_style_merge_equals_direct_construction(merged: waxy.Style, direct: waxy.Style) -> None:
    assert merged == direct
    assert hash(merged) == hash(direct)


def test_style_merge_after_hashing_left_operand_hashes_like_direct_construction() -> None:
    left = waxy.Style(flex_grow=1)
    hash(left)
    merged = left | waxy.Style(flex_shrink=2)
    assert hash(merged) == hash(waxy.Style(flex_grow=1, flex_shrink=2))


def test_tree_style_equals_style_with_every_field_passed() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(flex_grow=2))
    stored = tree.style(node)
    every_field = style_from_keywords(**{name: getattr(stored, name) for name in FIELD_NAMES})
    assert stored == every_field


def test_style_repr_of_empty_style() -> None:
    assert repr(waxy.Style()) == "Style()"


def test_style_repr_lists_set_fields_in_declaration_order() -> None:
    s = waxy.Style(border_top=waxy.Length(1), flex_grow=1)
    assert repr(s) == "Style(border_top=Length(1), flex_grow=1.0)"


@pytest.mark.parametrize(
    "style",
    [
        waxy.Style(),
        waxy.Style(display=waxy.Display.Block, flex_grow=1.5, margin_left=waxy.AUTO),
        waxy.Style(align_items=None, aspect_ratio=None),
        waxy.Style(size_width=waxy.FitContent(waxy.Percent(0.5)), flex_basis=waxy.CONTENT),
        style_from_keywords(**NON_DEFAULT_VALUES),
    ],
    ids=repr,
)
def test_style_repr_round_trips_through_eval(style: waxy.Style) -> None:
    assert eval(repr(style), vars(waxy)) == style


def test_style_fields_set_matches_keywords() -> None:
    s = waxy.Style(display=waxy.Display.Grid, align_items=None, flex_grow=0)
    assert s.fields_set == {"display", "align_items", "flex_grow"}


def test_style_fields_set_is_empty_for_empty_style() -> None:
    assert waxy.Style().fields_set == frozenset()


def test_style_fields_set_of_merge_is_union() -> None:
    a = waxy.Style(display=waxy.Display.Grid, flex_grow=1)
    b = waxy.Style(flex_grow=2, padding_top=waxy.Length(1))
    assert (a | b).fields_set == a.fields_set | b.fields_set
