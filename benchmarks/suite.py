# Every case calls its operation through one lambda, even where the lambda could be dropped,
# so each case pays the same call overhead and the cases compare on equal footing.
# ruff: noqa: PLW0108

"""
Time every operation a frame-by-frame caller performs, and compare runs against a baseline.

Run against a release build (`just bench` builds one first):

```text
just bench                                      # every case
just bench-args="-k style" bench                # cases whose name contains "style"
just bench-args="--save /tmp/before.json" bench # also write the results
just bench-args="--compare /tmp/before.json" bench
```

Each case reports the best per-call time over several runs,
each run long enough for `timeit` to calibrate.
A comparison against results saved earlier also absorbs whatever else the machine was doing in
between; `ab.py` alternates two builds instead.
"""

import argparse
import itertools
import json
import math
import timeit
from collections.abc import Callable
from pathlib import Path

from workloads import (
    CARD_STYLE,
    DASHBOARD_AVAILABLE,
    GRID_STYLE_KWARGS,
    ROW_STYLE,
    TEXT_STYLE,
    TYPICAL_STYLE_KWARGS,
    build_dashboard,
    build_deep,
    build_grid,
    build_text_column,
    build_wide,
    format_time,
    measure_text,
)

import waxy

type Case = tuple[str, Callable[[], object]]


def geometry_cases() -> list[Case]:
    """Constructing, reading, hashing and combining the small geometry types."""
    size = waxy.Size(3.0, 4.0)
    other_size = waxy.Size(3.0, 4.0)
    point = waxy.Point(1.0, 2.0)
    known = waxy.KnownSize(3.0, None)
    available_definite = waxy.AvailableSize(waxy.Definite(120), waxy.MAX_CONTENT)
    available_content = waxy.AvailableSize(waxy.MIN_CONTENT, waxy.MAX_CONTENT)
    definite = waxy.Definite(120)
    return [
        ("geometry: Size(w, h)", lambda: waxy.Size(3.0, 4.0)),
        ("geometry: Size(width=, height=)", lambda: waxy.Size(width=3.0, height=4.0)),
        ("geometry: Point(x, y)", lambda: waxy.Point(3.0, 4.0)),
        ("geometry: Rect(l, r, t, b)", lambda: waxy.Rect(1.0, 2.0, 3.0, 4.0)),
        ("geometry: KnownSize(w, None)", lambda: waxy.KnownSize(3.0, None)),
        (
            "geometry: AvailableSize(Definite, MAX_CONTENT)",
            lambda: waxy.AvailableSize(definite, waxy.MAX_CONTENT),
        ),
        ("geometry: size.width", lambda: size.width),
        ("geometry: known.width", lambda: known.width),
        ("geometry: available.width (Definite)", lambda: available_definite.width),
        ("geometry: available.width (MinContent)", lambda: available_content.width),
        ("geometry: hash(Size)", lambda: hash(size)),
        ("geometry: Size == Size", lambda: size == other_size),
        ("geometry: Point + Point", lambda: point + point),
        ("geometry: repr(Size)", lambda: repr(size)),
    ]


def value_cases() -> list[Case]:
    """Constructing and comparing the value types that go into a `Style`."""
    length = waxy.Length(1)
    other_length = waxy.Length(1)
    return [
        ("values: Length(1)", lambda: waxy.Length(1)),
        ("values: Percent(0.5)", lambda: waxy.Percent(0.5)),
        ("values: Fraction(1)", lambda: waxy.Fraction(1)),
        ("values: Minmax(Length, Fraction)", lambda: waxy.Minmax(waxy.Length(5), waxy.Fraction(2))),
        ("values: Repeat(3, [Length])", lambda: waxy.Repeat(3, [length])),
        (
            "values: GridPlacement(GridLine, GridSpan)",
            lambda: waxy.GridPlacement(waxy.GridLine(1), waxy.GridSpan(2)),
        ),
        ("values: hash(Length)", lambda: hash(length)),
        ("values: Length == Length", lambda: length == other_length),
    ]


def style_cases() -> list[Case]:
    """Constructing, merging, hashing, comparing and reading `Style`."""
    typical = waxy.Style(**TYPICAL_STYLE_KWARGS)  # type: ignore[arg-type]
    other_typical = waxy.Style(**TYPICAL_STYLE_KWARGS)  # type: ignore[arg-type]
    grid = waxy.Style(**GRID_STYLE_KWARGS)  # type: ignore[arg-type]
    override = waxy.Style(flex_grow=2.0, margin_top=waxy.Length(1))
    length = waxy.Length(1)
    percent = waxy.Percent(1.0)
    return [
        ("style: Style()", lambda: waxy.Style()),
        ("style: Style(flex_grow=1)", lambda: waxy.Style(flex_grow=1)),
        # The size_width cases take a value from the first, second, third and last positions of
        # its union, since extraction tries the union's types in order.
        ("style: Style(size_width=Length)", lambda: waxy.Style(size_width=length)),
        ("style: Style(size_width=Percent)", lambda: waxy.Style(size_width=percent)),
        ("style: Style(size_width=AUTO)", lambda: waxy.Style(size_width=waxy.AUTO)),
        ("style: Style(size_width=STRETCH)", lambda: waxy.Style(size_width=waxy.STRETCH)),
        ("style: Style(typical, 11 fields)", lambda: waxy.Style(**TYPICAL_STYLE_KWARGS)),  # type: ignore[arg-type]
        ("style: Style(grid, 7 tracks)", lambda: waxy.Style(**GRID_STYLE_KWARGS)),  # type: ignore[arg-type]
        ("style: a | b", lambda: typical | override),
        ("style: hash(a | b)", lambda: hash(typical | override)),
        ("style: hash, cached", lambda: hash(typical)),
        ("style: == equal", lambda: typical == other_typical),
        ("style: .flex_grow", lambda: typical.flex_grow),
        ("style: .padding_left", lambda: typical.padding_left),
        ("style: .display", lambda: typical.display),
        ("style: .grid_template_columns", lambda: grid.grid_template_columns),
        ("style: .fields_set", lambda: typical.fields_set),
        ("style: repr(typical)", lambda: repr(typical)),
    ]


def tree_cases() -> list[Case]:
    """Building, editing and querying a `TaffyTree`, one operation at a time."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, leaves = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
    row = tree.children(root)[0]
    card = tree.children(row)[0]
    card_children = tree.children(card)
    leaf = leaves[0]
    styles = itertools.cycle([CARD_STYLE, ROW_STYLE])
    texts = itertools.cycle(["Changed text", "Other text"])

    def new_leaf_and_remove() -> None:
        tree.remove(tree.new_leaf(TEXT_STYLE))

    def new_leaf_with_context_and_remove() -> None:
        tree.remove(tree.new_leaf_with_context(TEXT_STYLE, "text"))

    def new_tree_with_six_leaves() -> None:
        scratch: waxy.TaffyTree[str] = waxy.TaffyTree()
        children = [scratch.new_leaf(TEXT_STYLE) for _ in range(6)]
        scratch.new_with_children(ROW_STYLE, children)

    return [
        ("tree: TaffyTree()", lambda: waxy.TaffyTree()),
        ("tree: new_leaf + remove", new_leaf_and_remove),
        ("tree: new_leaf_with_context + remove", new_leaf_with_context_and_remove),
        ("tree: new tree, 6 leaves, new_with_children", new_tree_with_six_leaves),
        ("tree: set_children (same children)", lambda: tree.set_children(card, card_children)),
        ("tree: children", lambda: tree.children(row)),
        ("tree: child_count", lambda: tree.child_count(row)),
        ("tree: child_at_index", lambda: tree.child_at_index(row, 0)),
        ("tree: parent", lambda: tree.parent(leaf)),
        ("tree: style", lambda: tree.style(card)),
        ("tree: set_style (equal)", lambda: tree.set_style(card, CARD_STYLE)),
        ("tree: set_style (changed)", lambda: tree.set_style(card, next(styles))),
        ("tree: get_node_context", lambda: tree.get_node_context(leaf)),
        ("tree: set_node_context", lambda: tree.set_node_context(leaf, next(texts))),
        ("tree: dirty", lambda: tree.dirty(leaf)),
        ("tree: mark_dirty", lambda: tree.mark_dirty(leaf)),
        ("tree: layout", lambda: tree.layout(card)),
        ("tree: unrounded_layout", lambda: tree.unrounded_layout(card)),
    ]


def layout_cases() -> list[Case]:
    """Reading a computed `Layout` and the whole tree's layouts."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
    layout = tree.layout(tree.children(tree.children(root)[0])[0])

    def recurse(node: waxy.NodeId, origin: waxy.Point, out: list[object]) -> None:
        node_layout = tree.layout(node)
        position = origin + node_layout.location
        out.append((node, position, node_layout))
        for child in tree.children(node):
            recurse(child, position, out)

    return [
        ("layout: .location", lambda: layout.location),
        ("layout: .size", lambda: layout.size),
        ("layout: .margin", lambda: layout.margin),
        ("layout: .size.width", lambda: layout.size.width),
        ("layout: .content_box_width()", lambda: layout.content_box_width()),
        ("layout: dashboard, absolute_layouts", lambda: tree.absolute_layouts(root)),
        ("layout: dashboard, Python recursion", lambda: recurse(root, waxy.Point(), [])),
        ("layout: dashboard, format_tree", lambda: tree.format_tree(root)),
    ]


def compute_cases() -> list[Case]:
    """Building and computing whole trees, from scratch and reused across frames."""

    def build_only(build: Callable[[waxy.TaffyTree[str]], object]) -> Callable[[], object]:
        return lambda: build(waxy.TaffyTree())

    def build_and_compute(
        build: Callable[[waxy.TaffyTree[str]], waxy.NodeId], *, with_measure: bool = True
    ) -> Callable[[], None]:
        def frame() -> None:
            tree: waxy.TaffyTree[str] = waxy.TaffyTree()
            root = build(tree)
            if with_measure:
                tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
            else:
                tree.compute_layout(root, DASHBOARD_AVAILABLE)

        return frame

    def dashboard_root(tree: waxy.TaffyTree[str]) -> waxy.NodeId:
        return build_dashboard(tree)[0]

    reused: waxy.TaffyTree[str] = waxy.TaffyTree()
    reused_root, reused_leaves = build_dashboard(reused)
    reused.compute_layout(reused_root, DASHBOARD_AVAILABLE, measure_text)
    reused_nodes = [reused_root]
    for node in reused_nodes:
        reused_nodes.extend(reused.children(node))
    reused_styles = [reused.style(node) for node in reused_nodes]
    texts = itertools.cycle(["Changed text", "Other text"])

    def reuse_change_one_leaf() -> None:
        reused.set_node_context(reused_leaves[0], next(texts))
        reused.compute_layout(reused_root, DASHBOARD_AVAILABLE, measure_text)

    def reuse_set_every_style() -> None:
        for node, style in zip(reused_nodes, reused_styles, strict=True):
            reused.set_style(node, style)
        reused.compute_layout(reused_root, DASHBOARD_AVAILABLE, measure_text)

    one_leaf: waxy.TaffyTree[str] = waxy.TaffyTree()
    measured_leaf = one_leaf.new_leaf_with_context(TEXT_STYLE, "text")
    shared_size = waxy.Size(4.0, 1.0)

    def constant_measure(
        _known: waxy.KnownSize, _available: waxy.AvailableSize, _text: str
    ) -> waxy.Size:
        return shared_size

    def remeasure_one_leaf() -> None:
        one_leaf.mark_dirty(measured_leaf)
        one_leaf.compute_layout(measured_leaf, DASHBOARD_AVAILABLE, constant_measure)

    return [
        ("compute: dashboard, build only", build_only(build_dashboard)),
        ("compute: dashboard, build + compute", build_and_compute(dashboard_root)),
        (
            "compute: dashboard, build + compute, no measure",
            build_and_compute(dashboard_root, with_measure=False),
        ),
        ("compute: dashboard, reused, change one leaf", reuse_change_one_leaf),
        ("compute: dashboard, reused, set every style", reuse_set_every_style),
        (
            "compute: dashboard, reused, clean",
            lambda: reused.compute_layout(reused_root, DASHBOARD_AVAILABLE, measure_text),
        ),
        ("compute: one leaf, remeasure", remeasure_one_leaf),
        ("compute: wide (1000 fixed leaves), build only", build_only(build_wide)),
        (
            "compute: wide (1000 fixed leaves), build + compute",
            build_and_compute(build_wide, with_measure=False),
        ),
        ("compute: deep (100 levels), build + compute", build_and_compute(build_deep)),
        ("compute: grid (100 text cells), build + compute", build_and_compute(build_grid)),
        (
            "compute: text column (200 leaves), build + compute",
            build_and_compute(build_text_column),
        ),
    ]


def all_cases() -> list[Case]:
    """Every case, grouped by area."""
    return (
        geometry_cases()
        + value_cases()
        + style_cases()
        + tree_cases()
        + layout_cases()
        + compute_cases()
    )


def time_case(fn: Callable[[], object], repeat: int) -> float:
    """Best per-call time of `fn` in seconds, over `repeat` calibrated runs."""
    timer = timeit.Timer(fn)
    number, _ = timer.autorange()
    return min(timer.repeat(repeat=repeat, number=number)) / number


def format_ratio(ratio: float) -> str:
    """Format a current-to-baseline time ratio, marking changes beyond noise."""
    if ratio <= 0.95:
        marker = "  faster"
    elif ratio >= 1.05:
        marker = "  SLOWER"
    else:
        marker = ""
    return f"{ratio:.2f}x{marker}"


def main() -> None:
    """Run the selected cases, print them, and optionally save or compare the results."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-k", "--filter", default="", help="only run cases whose name contains this"
    )
    parser.add_argument("--repeat", type=int, default=5, help="calibrated runs per case")
    parser.add_argument("--save", type=Path, help="write the results to this JSON file")
    parser.add_argument("--compare", type=Path, help="compare against results saved with --save")
    args = parser.parse_args()

    baseline: dict[str, float] = json.loads(args.compare.read_text()) if args.compare else {}
    cases = [(name, fn) for name, fn in all_cases() if args.filter in name]
    width = max(len(name) for name, _ in cases)

    results: dict[str, float] = {}
    ratios: list[float] = []
    for name, fn in cases:
        seconds = time_case(fn, args.repeat)
        results[name] = seconds
        line = f"{name:<{width}}  {format_time(seconds):>10}"
        if (before := baseline.get(name)) is not None:
            ratio = seconds / before
            ratios.append(ratio)
            line += f"  {format_time(before):>10}  {format_ratio(ratio)}"
        print(line, flush=True)

    if ratios:
        geometric_mean = math.exp(sum(map(math.log, ratios)) / len(ratios))
        print(f"\ngeometric mean of {len(ratios)} ratios: {geometric_mean:.2f}x")
    if args.save:
        args.save.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
