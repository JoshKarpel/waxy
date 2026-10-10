"""
Shared workloads and timing for the benchmark scripts in this directory.

Run the scripts against a release build (`just bench-build`),
since a debug build's timings say nothing about what users see.
"""

import math
import timeit
from collections.abc import Callable

import waxy

TYPICAL_STYLE_KWARGS: dict[str, object] = {
    "display": waxy.Display.Flex,
    "flex_direction": waxy.FlexDirection.Column,
    "flex_grow": 1.0,
    "padding_left": waxy.Length(1),
    "padding_right": waxy.Length(1),
    "padding_top": waxy.Length(1),
    "padding_bottom": waxy.Length(1),
    "border_left": waxy.Length(1),
    "border_right": waxy.Length(1),
    "border_top": waxy.Length(1),
    "border_bottom": waxy.Length(1),
}
"""A style with 11 fields set, shaped like a bordered, padded card."""

GRID_STYLE_KWARGS: dict[str, object] = {
    "display": waxy.Display.Grid,
    "grid_template_columns": [
        waxy.Length(10),
        waxy.Fraction(1),
        waxy.Percent(0.2),
        waxy.AUTO,
        waxy.Minmax(waxy.Length(5), waxy.Fraction(2)),
        waxy.MIN_CONTENT,
        waxy.MAX_CONTENT,
    ],
}
"""A grid container with 7 template tracks."""

DASHBOARD_AVAILABLE = waxy.AvailableSize(waxy.Definite(120), waxy.Definite(40))

ROOT_STYLE = waxy.Style(
    flex_direction=waxy.FlexDirection.Column,
    size_width=waxy.Percent(1.0),
    size_height=waxy.Percent(1.0),
)
ROW_STYLE = waxy.Style(flex_direction=waxy.FlexDirection.Row, flex_grow=1.0)
CARD_STYLE = waxy.Style(**TYPICAL_STYLE_KWARGS)  # type: ignore[arg-type]
TEXT_STYLE = waxy.Style()


def measure_text(known: waxy.KnownSize, available: waxy.AvailableSize, text: str) -> waxy.Size:
    """Measure `text` as a single paragraph wrapped to the width taffy offers, one cell per char."""
    if known.width is not None:
        width = known.width
    elif isinstance(available.width, waxy.Definite):
        width = min(float(len(text)), available.width.value)
    else:
        width = float(len(text))
    lines = math.ceil(len(text) / width) if width > 0 else len(text)
    return waxy.Size(width, float(lines))


def build_dashboard(tree: waxy.TaffyTree[str]) -> tuple[waxy.NodeId, list[waxy.NodeId]]:
    """
    Build a 39-node tree shaped like counterweight's dashboard.

    Two rows of six cards, each card a column of two text leaves (24 leaves in all).
    Returns the root and the leaves.
    """
    leaves = []
    rows = []
    for row_index in range(2):
        cards = []
        for card_index in range(6):
            title = tree.new_leaf_with_context(TEXT_STYLE, f"Card {row_index}.{card_index}")
            body = tree.new_leaf_with_context(
                TEXT_STYLE, f"Some body text for card {row_index}.{card_index}"
            )
            leaves += [title, body]
            cards.append(tree.new_with_children(CARD_STYLE, [title, body]))
        rows.append(tree.new_with_children(ROW_STYLE, cards))
    root = tree.new_with_children(ROOT_STYLE, rows)
    return root, leaves


FIXED_LEAF_STYLE = waxy.Style(size_width=waxy.Length(4), size_height=waxy.Length(1))
WRAP_ROW_STYLE = waxy.Style(
    flex_direction=waxy.FlexDirection.Row,
    flex_wrap=waxy.FlexWrap.Wrap,
    size_width=waxy.Length(120),
)
COLUMN_STYLE = waxy.Style(flex_direction=waxy.FlexDirection.Column, size_width=waxy.Length(80))
NESTED_STYLE = waxy.Style(
    padding_left=waxy.Length(1),
    padding_top=waxy.Length(1),
    flex_grow=1.0,
)
GRID_CONTAINER_STYLE = waxy.Style(
    display=waxy.Display.Grid,
    grid_template_columns=[waxy.Repeat(10, [waxy.Fraction(1)])],
    size_width=waxy.Length(120),
)


def build_wide(tree: waxy.TaffyTree[str], leaf_count: int = 1_000) -> waxy.NodeId:
    """Build a wrapping row of `leaf_count` fixed-size leaves, with no measured content."""
    leaves = [tree.new_leaf(FIXED_LEAF_STYLE) for _ in range(leaf_count)]
    return tree.new_with_children(WRAP_ROW_STYLE, leaves)


def build_deep(tree: waxy.TaffyTree[str], depth: int = 100) -> waxy.NodeId:
    """Build a chain of `depth` padded nodes ending in one text leaf."""
    node = tree.new_leaf_with_context(TEXT_STYLE, "The innermost text")
    for _ in range(depth):
        node = tree.new_with_children(NESTED_STYLE, [node])
    return node


def build_grid(tree: waxy.TaffyTree[str], cell_count: int = 100) -> waxy.NodeId:
    """Build a 10-column grid of `cell_count` text leaves."""
    cells = [
        tree.new_leaf_with_context(TEXT_STYLE, f"Cell number {index}")
        for index in range(cell_count)
    ]
    return tree.new_with_children(GRID_CONTAINER_STYLE, cells)


def build_text_column(tree: waxy.TaffyTree[str], leaf_count: int = 200) -> waxy.NodeId:
    """Build a column of `leaf_count` text leaves of varying length, so measuring dominates."""
    leaves = [
        tree.new_leaf_with_context(TEXT_STYLE, "word " * (1 + index % 40))
        for index in range(leaf_count)
    ]
    return tree.new_with_children(COLUMN_STYLE, leaves)


def best_of(fn: Callable[[], object], number: int, repeat: int = 5) -> float:
    """Best per-call time of `fn` in seconds, over `repeat` runs of `number` calls."""
    return min(timeit.repeat(fn, number=number, repeat=repeat)) / number


def format_time(seconds: float) -> str:
    """Format a per-call time in the unit that keeps it readable."""
    if seconds >= 1e-3:
        return f"{seconds * 1e3:.2f} ms"
    if seconds >= 1e-6:
        return f"{seconds * 1e6:.1f} µs"
    return f"{seconds * 1e9:.0f} ns"


def report(rows: list[tuple[str, str]]) -> None:
    """Print `(label, value)` rows as an aligned table."""
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"{label:<{width}}  {value}")
