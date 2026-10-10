"""
Measure the ratios behind each claim on the docs' performance page (plan item 10).

Each section prints both sides of a comparison and the ratio between them,
since the ratio is what the page states.
"""

from workloads import (
    DASHBOARD_AVAILABLE,
    TYPICAL_STYLE_KWARGS,
    best_of,
    build_dashboard,
    format_time,
    measure_text,
    report,
)

import waxy


def compare(label: str, slow: float, fast: float) -> list[tuple[str, str]]:
    """Rows for one comparison: each side's time and the ratio of the fast to the slow."""
    return [
        (f"{label}: slow", format_time(slow)),
        (f"{label}: fast", format_time(fast)),
        (f"{label}: fast / slow", f"{fast / slow:.2f}"),
    ]


def construct_vs_merge() -> list[tuple[str, str]]:
    """Constructing a typical style against merging two prebuilt ones."""
    a = waxy.Style(**TYPICAL_STYLE_KWARGS)  # type: ignore[arg-type]
    b = waxy.Style(flex_grow=2.0)
    return compare(
        "construct typical style vs merge",
        best_of(lambda: waxy.Style(**TYPICAL_STYLE_KWARGS), 200_000),  # type: ignore[arg-type]
        best_of(lambda: a | b, 200_000),
    )


def layout_field_access() -> list[tuple[str, str]]:
    """Reading four sides of `margin` through the property each time, or through a local."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
    layout = tree.layout(root)

    def repeated() -> float:
        return layout.margin.left + layout.margin.right + layout.margin.top + layout.margin.bottom

    def bound() -> float:
        m = layout.margin
        return m.left + m.right + m.top + m.bottom

    return compare("margin sides", best_of(repeated, 500_000), best_of(bound, 500_000))


def shared_size() -> list[tuple[str, str]]:
    """Returning a new `Size` from a measure callback against returning a shared one."""
    shared = waxy.Size(3.0, 4.0)
    return compare(
        "measure result",
        best_of(lambda: waxy.Size(3.0, 4.0), 1_000_000),
        best_of(lambda: shared, 1_000_000),
    )


def positional_arguments() -> list[tuple[str, str]]:
    """Constructing small value types by keyword against positionally."""
    return [
        *compare(
            "Size args",
            best_of(lambda: waxy.Size(width=3.0, height=4.0), 1_000_000),
            best_of(lambda: waxy.Size(3.0, 4.0), 1_000_000),
        ),
        *compare(
            "Point args",
            best_of(lambda: waxy.Point(x=3.0, y=4.0), 1_000_000),
            best_of(lambda: waxy.Point(3.0, 4.0), 1_000_000),
        ),
        *compare(
            "KnownSize args",
            best_of(lambda: waxy.KnownSize(width=3.0, height=4.0), 1_000_000),
            best_of(lambda: waxy.KnownSize(3.0, 4.0), 1_000_000),
        ),
        *compare(
            "AvailableSize args",
            best_of(lambda: waxy.AvailableSize(width=MIN, height=MAX), 1_000_000),
            best_of(lambda: waxy.AvailableSize(MIN, MAX), 1_000_000),
        ),
        *compare(
            "Length args",
            best_of(lambda: waxy.Length(value=3.0), 1_000_000),
            best_of(lambda: waxy.Length(3.0), 1_000_000),
        ),
    ]


MIN = waxy.MIN_CONTENT
MAX = waxy.MAX_CONTENT


def reuse_tree() -> list[tuple[str, str]]:
    """Building and computing a new tree against setting every style on a reused one."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
    nodes = [root]
    for node in nodes:
        nodes.extend(tree.children(node))
    styles = [tree.style(node) for node in nodes]

    def new_tree() -> None:
        fresh: waxy.TaffyTree[str] = waxy.TaffyTree()
        fresh_root, _ = build_dashboard(fresh)
        fresh.compute_layout(fresh_root, DASHBOARD_AVAILABLE, measure_text)

    def reused() -> None:
        for node, style in zip(nodes, styles, strict=True):
            tree.set_style(node, style)
        tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)

    return compare(
        "new tree vs reused, nothing changed", best_of(new_tree, 2_000), best_of(reused, 2_000)
    )


if __name__ == "__main__":
    report(
        reuse_tree()
        + construct_vs_merge()
        + layout_field_access()
        + shared_size()
        + positional_arguments()
    )
