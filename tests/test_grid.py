"""Tests for grid repetition, named lines, template areas, and detailed grid layout info."""

import pytest

import waxy

L = waxy.Length

# --- Repeat ---


def test_repeat_construction() -> None:
    r = waxy.Repeat(3, [L(10.0), waxy.Fraction(2.0)], [["a"], ["b"], ["c"]])
    assert r.count == 3
    assert r.tracks == [L(10.0), waxy.Fraction(2.0)]
    assert r.line_names == [["a"], ["b"], ["c"]]


def test_repeat_line_names_default_empty() -> None:
    assert waxy.Repeat(2, [L(10.0)]).line_names == []


@pytest.mark.parametrize("count", [waxy.AUTO_FILL, waxy.AUTO_FIT], ids=repr)
def test_repeat_auto_count(count: waxy.AutoFill | waxy.AutoFit) -> None:
    assert waxy.Repeat(count, [L(10.0)]).count == count


@pytest.mark.parametrize(
    ("repeat", "expected"),
    [
        (waxy.Repeat(2, [L(10.0)]), "Repeat(2, [Length(10)])"),
        (waxy.Repeat(waxy.AUTO_FIT, [L(5.0)]), "Repeat(AutoFit(), [Length(5)])"),
        (
            waxy.Repeat(1, [L(5.0)], [["a"], []]),
            "Repeat(1, [Length(5)], line_names=[['a'], []])",
        ),
    ],
)
def test_repeat_repr(repeat: waxy.Repeat, expected: str) -> None:
    assert repr(repeat) == expected


def test_repeat_eq_and_hash() -> None:
    a = waxy.Repeat(2, [L(10.0)], [["x"], ["y"]])
    b = waxy.Repeat(2, [L(10.0)], [["x"], ["y"]])
    assert a == b
    assert hash(a) == hash(b)
    assert a != waxy.Repeat(3, [L(10.0)], [["x"], ["y"]])
    assert a != waxy.Repeat(2, [L(11.0)], [["x"], ["y"]])
    assert a != waxy.Repeat(2, [L(10.0)], [["x"], ["z"]])


def test_repeat_match() -> None:
    match waxy.Repeat(4, [L(7.0)]):
        case waxy.Repeat(count, [waxy.Length(size)], []):
            assert (count, size) == (4, 7.0)
        case _:
            pytest.fail("pattern match failed")


@pytest.mark.parametrize(
    ("count", "tracks", "line_names", "message"),
    [
        (0, [L(1.0)], None, "count must be at least 1"),
        (1, [], None, "at least one track"),
        (1, [L(1.0)], [["a"]], "len\\(tracks\\) \\+ 1 = 2"),
        (1, [L(1.0)], [["a"], ["b"], ["c"]], "len\\(tracks\\) \\+ 1 = 2"),
    ],
)
def test_repeat_invalid_raises(
    count: int, tracks: list[waxy.GridTrackValue], line_names: list[list[str]] | None, message: str
) -> None:
    with pytest.raises(waxy.InvalidRepeat, match=message):
        waxy.Repeat(count, tracks, line_names)


def test_repeat_rejects_nested_repeat() -> None:
    with pytest.raises(TypeError):
        waxy.Repeat(2, [waxy.Repeat(2, [L(1.0)])])  # type: ignore[list-item]


def test_style_grid_template_round_trips_repeat() -> None:
    columns: list[waxy.GridTemplateValue] = [
        L(100.0),
        waxy.Repeat(waxy.AUTO_FILL, [L(50.0)], [["a"], ["b"]]),
        waxy.Fraction(1.0),
    ]
    assert waxy.Style(grid_template_columns=columns).grid_template_columns == columns


def test_repeat_count_lays_out_tracks() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    children = [tree.new_leaf(waxy.Style()) for _ in range(3)]
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[waxy.Repeat(3, [L(40.0)])],
        ),
        children,
    )
    tree.compute_layout(root)
    assert [tree.layout(c).location.x for c in children] == [0.0, 40.0, 80.0]


def test_repeat_auto_fill_fits_container() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            size_width=L(130.0),
            grid_template_columns=[waxy.Repeat(waxy.AUTO_FILL, [L(40.0)])],
        ),
        [tree.new_leaf(waxy.Style())],
    )
    tree.compute_layout(root)
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.columns.explicit_tracks == 3


# --- Named lines ---


def test_named_grid_line_defaults_index_to_none() -> None:
    assert waxy.NamedGridLine("a").index is None


def test_named_grid_span_defaults_count_to_1() -> None:
    assert waxy.NamedGridSpan("a").count == 1


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (waxy.NamedGridLine("a", -2), "NamedGridLine('a', -2)"),
        (waxy.NamedGridLine("a"), "NamedGridLine('a')"),
        (waxy.NamedGridSpan("b", 3), "NamedGridSpan('b', 3)"),
    ],
)
def test_named_placement_repr(value: object, expected: str) -> None:
    assert repr(value) == expected


def test_named_grid_line_eq_and_hash() -> None:
    assert waxy.NamedGridLine("a", 2) == waxy.NamedGridLine("a", 2)
    assert hash(waxy.NamedGridLine("a", 2)) == hash(waxy.NamedGridLine("a", 2))
    assert waxy.NamedGridLine("a", 2) != waxy.NamedGridLine("a", 3)
    assert waxy.NamedGridLine("a", 2) != waxy.NamedGridLine("b", 2)


def test_named_grid_line_zero_index_raises() -> None:
    with pytest.raises(waxy.InvalidGridLine):
        waxy.NamedGridLine("a", 0)


def test_named_grid_span_zero_count_raises() -> None:
    with pytest.raises(waxy.InvalidGridSpan):
        waxy.NamedGridSpan("a", 0)


def test_grid_placement_round_trips_named_values() -> None:
    placement = waxy.GridPlacement(waxy.NamedGridLine("a", 2), waxy.NamedGridSpan("b", 3))
    style = waxy.Style(grid_column=placement)
    assert style.grid_column.start == waxy.NamedGridLine("a", 2)
    assert style.grid_column.end == waxy.NamedGridSpan("b", 3)


def test_style_line_names_round_trip() -> None:
    names = [["left"], ["middle", "center"], ["right"]]
    style = waxy.Style(grid_template_row_names=names, grid_template_column_names=names[::-1])
    assert style.grid_template_row_names == names
    assert style.grid_template_column_names == names[::-1]


def test_style_line_names_affect_eq_and_hash() -> None:
    a = waxy.Style(grid_template_column_names=[["x"]])
    assert a != waxy.Style()
    assert hash(a) != hash(waxy.Style())


def test_item_placed_by_named_lines() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(
        waxy.Style(
            grid_column=waxy.GridPlacement(
                waxy.NamedGridLine("content"), waxy.NamedGridLine("content-end")
            )
        )
    )
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[L(10.0), L(20.0), L(30.0)],
            grid_template_column_names=[[], ["content"], [], ["content-end"]],
        ),
        [child],
    )
    tree.compute_layout(root)
    layout = tree.layout(child)
    assert (layout.location.x, layout.size.width) == (10.0, 50.0)


def test_item_placed_by_named_lines_inside_repeat() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(
        waxy.Style(grid_column=waxy.GridPlacement(waxy.NamedGridLine("col", 3), waxy.GridSpan(1)))
    )
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[waxy.Repeat(4, [L(25.0)], [["col"], []])],
            grid_template_column_names=[[], []],
        ),
        [child],
    )
    tree.compute_layout(root)
    assert tree.layout(child).location.x == 50.0


# --- Template areas ---


def test_grid_template_area_construction() -> None:
    area = waxy.GridTemplateArea("main", 2, 4, 1, 3)
    assert (area.name, area.row_start, area.row_end, area.column_start, area.column_end) == (
        "main",
        2,
        4,
        1,
        3,
    )


def test_grid_template_area_repr() -> None:
    assert repr(waxy.GridTemplateArea("a", 1, 2, 3, 4)) == "GridTemplateArea('a', 1, 2, 3, 4)"


@pytest.mark.parametrize(
    "bounds",
    [(0, 1, 1, 2), (1, 2, 0, 1), (2, 2, 1, 2), (1, 2, 3, 2)],
)
def test_grid_template_area_invalid_raises(bounds: tuple[int, int, int, int]) -> None:
    with pytest.raises(waxy.InvalidGridTemplateArea):
        waxy.GridTemplateArea("a", *bounds)


def test_grid_template_areas_from_strings() -> None:
    areas = waxy.GridTemplateAreas.from_strings(["header header", "nav main", ". main"])
    assert areas == waxy.GridTemplateAreas(
        [
            waxy.GridTemplateArea("header", 1, 2, 1, 3),
            waxy.GridTemplateArea("nav", 2, 3, 1, 2),
            waxy.GridTemplateArea("main", 2, 4, 2, 3),
        ],
        3,
        2,
    )


def test_grid_template_areas_from_strings_counts_unnamed_cells() -> None:
    areas = waxy.GridTemplateAreas.from_strings(["a ... .", "a . ."])
    assert (areas.row_count, areas.column_count) == (2, 3)
    assert areas.areas == [waxy.GridTemplateArea("a", 1, 3, 1, 2)]


def test_grid_template_areas_from_strings_splits_name_from_dots() -> None:
    areas = waxy.GridTemplateAreas.from_strings(["a.b"])
    assert [a.name for a in areas.areas] == ["a", "b"]
    assert areas.column_count == 3


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([], "at least one row"),
        (["a b", "a"], "same number of cells"),
        (["a b", "b a"], "not a rectangle"),
        (["a b a"], "not a rectangle"),
        (["   "], "has no cells"),
        (["a!"], "invalid character"),
    ],
)
def test_grid_template_areas_from_strings_invalid_raises(rows: list[str], message: str) -> None:
    with pytest.raises(waxy.InvalidGridTemplateAreas, match=message):
        waxy.GridTemplateAreas.from_strings(rows)


def test_grid_template_areas_area_out_of_bounds_raises() -> None:
    with pytest.raises(waxy.InvalidGridTemplateAreas, match="extends past"):
        waxy.GridTemplateAreas([waxy.GridTemplateArea("a", 1, 3, 1, 2)], 1, 1)


def test_grid_template_areas_duplicate_name_raises() -> None:
    area = waxy.GridTemplateArea("a", 1, 2, 1, 2)
    with pytest.raises(waxy.InvalidGridTemplateAreas, match="more than one"):
        waxy.GridTemplateAreas([area, area], 1, 1)


def test_grid_template_areas_eq_and_hash() -> None:
    a = waxy.GridTemplateAreas.from_strings(["a b"])
    b = waxy.GridTemplateAreas.from_strings(["a b"])
    assert a == b
    assert hash(a) == hash(b)
    assert a != waxy.GridTemplateAreas.from_strings(["a b ."])


def test_style_grid_template_areas_round_trips() -> None:
    areas = waxy.GridTemplateAreas.from_strings(["a b"])
    assert waxy.Style(grid_template_areas=areas).grid_template_areas == areas
    assert waxy.Style().grid_template_areas is None


def test_style_grid_template_areas_none_clears_in_merge() -> None:
    areas = waxy.GridTemplateAreas.from_strings(["a"])
    merged = waxy.Style(grid_template_areas=areas) | waxy.Style(grid_template_areas=None)
    assert merged.grid_template_areas is None


def test_item_placed_into_named_area() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(
        waxy.Style(
            grid_row=waxy.GridPlacement(waxy.NamedGridLine("main"), waxy.NamedGridLine("main")),
            grid_column=waxy.GridPlacement(waxy.NamedGridLine("main"), waxy.NamedGridLine("main")),
        )
    )
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[L(30.0), L(70.0)],
            grid_template_rows=[L(10.0), L(20.0), L(40.0)],
            grid_template_areas=waxy.GridTemplateAreas.from_strings(
                ["head head", "nav main", ". main"]
            ),
        ),
        [child],
    )
    tree.compute_layout(root)
    layout = tree.layout(child)
    assert (layout.location, layout.size) == (waxy.Point(30.0, 10.0), waxy.Size(70.0, 60.0))


def test_indexed_named_line_skips_grid_area_edges() -> None:
    """`1 main` counts lines named `main` itself, so it lands past the explicit grid."""
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf(
        waxy.Style(grid_column=waxy.GridPlacement(waxy.NamedGridLine("main", 1), waxy.GridSpan(1)))
    )
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[L(30.0), L(70.0)],
            grid_template_areas=waxy.GridTemplateAreas.from_strings(["nav main"]),
        ),
        [child],
    )
    tree.compute_layout(root)
    # Not at x=30, the `main` area's start edge, but past the explicit grid's end at x=100.
    assert tree.layout(child).location.x == 100.0


# --- Detailed layout info ---


def grid_with_two_items() -> tuple[waxy.TaffyTree[object], waxy.NodeId, list[waxy.NodeId]]:
    """A 3x2 grid with named lines, a gap, padding, and two items."""
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    first = tree.new_leaf(
        waxy.Style(grid_column=waxy.GridPlacement(waxy.GridLine(1), waxy.GridSpan(2)))
    )
    second = tree.new_leaf(waxy.Style(grid_row=waxy.GridPlacement(waxy.GridLine(2))))
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            grid_template_columns=[L(10.0), L(20.0), L(30.0)],
            grid_template_column_names=[["start"], [], [], ["end"]],
            grid_template_rows=[L(5.0), L(15.0)],
            gap_width=L(2.0),
            padding_left=L(1.0),
            padding_top=L(3.0),
        ),
        [first, second],
    )
    tree.compute_layout(root)
    return tree, root, [first, second]


def test_detailed_layout_info_none_for_non_grid() -> None:
    tree, _, children = grid_with_two_items()
    assert tree.detailed_layout_info(children[0]) is None


def test_detailed_layout_info_none_after_grid_becomes_flex() -> None:
    tree, root, _ = grid_with_two_items()
    tree.set_style(root, waxy.Style(display=waxy.Display.Flex))
    tree.compute_layout(root)
    assert tree.detailed_layout_info(root) is None


def test_detailed_layout_info_none_after_grid_loses_its_children() -> None:
    tree, root, _ = grid_with_two_items()
    tree.set_children(root, [])
    tree.compute_layout(root)
    assert tree.detailed_layout_info(root) is None


def test_detailed_layout_info_track_counts() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    columns = info.columns
    assert (
        columns.negative_implicit_tracks,
        columns.explicit_tracks,
        columns.positive_implicit_tracks,
    ) == (0, 3, 0)
    assert info.rows.explicit_tracks == 2


def test_detailed_layout_info_positions_include_padding_and_gaps() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.columns.positions == [
        waxy.Line(1.0, 11.0),
        waxy.Line(13.0, 33.0),
        waxy.Line(35.0, 65.0),
    ]


def test_detailed_layout_info_collapsed_tracks() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            size_width=L(100.0),
            grid_template_columns=[waxy.Repeat(waxy.AUTO_FIT, [L(20.0)])],
        ),
        [tree.new_leaf(waxy.Style())],
    )
    tree.compute_layout(root)
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.columns.collapsed_tracks == [range(1, 5)]


def test_detailed_layout_info_collapsed_tracks_empty_without_auto_fit() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.columns.collapsed_tracks == []


def test_detailed_layout_info_empty_axis_line_follows_content_alignment() -> None:
    """An absolute child creates no tracks, leaving each axis one line placed by alignment."""
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    root = tree.new_with_children(
        waxy.Style(
            display=waxy.Display.Grid,
            size_width=L(100.0),
            size_height=L(40.0),
            padding_left=L(3.0),
            padding_top=L(2.0),
            justify_content=waxy.AlignContent.End,
            align_content=waxy.AlignContent.Center,
        ),
        [tree.new_leaf(waxy.Style(position=waxy.Position.Absolute))],
    )
    tree.compute_layout(root)
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert (info.columns.empty_axis_line, info.rows.empty_axis_line) == (100.0, 21.0)


def test_detailed_layout_info_empty_axis_line_none_with_tracks() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert (info.columns.empty_axis_line, info.rows.empty_axis_line) == (None, None)


def test_detailed_layout_info_line_names() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.columns.line_names == [["start"], [], [], ["end"]]
    assert info.columns.names_for_line(3) == ["end"]
    assert info.columns.names_for_line(99) == []


def test_detailed_layout_info_serializes_templates() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.grid_template_columns() == "[start] 10px 20px 30px [end]"
    assert info.grid_template_rows() == "5px 15px"


def test_detailed_layout_info_items() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    first, second = info.items
    assert (first.row_start, first.row_end, first.column_start, first.column_end) == (1, 2, 1, 3)
    assert (second.row_start, second.row_end) == (2, 3)


def test_detailed_layout_info_item_grid_area() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    assert info.item_grid_area(0) == (waxy.Point(1.0, 3.0), waxy.Size(32.0, 5.0))


def test_detailed_layout_info_item_grid_area_out_of_range_raises() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    with pytest.raises(IndexError):
        info.item_grid_area(2)


def test_detailed_layout_info_resolve_absolute_grid_area() -> None:
    tree, root, _ = grid_with_two_items()
    info = tree.detailed_layout_info(root)
    assert info is not None
    area = info.resolve_absolute_grid_area(
        waxy.GridPlacement(waxy.GridLine(2), waxy.GridLine(3)),
        waxy.GridPlacement(waxy.NamedGridLine("start"), waxy.GridLine(2)),
        waxy.Direction.Ltr,
        waxy.Rect(left=1.0, right=65.0, top=3.0, bottom=25.0),
    )
    assert area == waxy.Rect(left=1.0, right=11.0, top=8.0, bottom=23.0)
