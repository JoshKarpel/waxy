"""
Shared workloads and timing for the benchmark scripts in this directory.

Run the scripts against a release build (`uv run maturin develop --release`),
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
