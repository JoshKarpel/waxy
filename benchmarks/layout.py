"""
Time laying out the dashboard-shaped tree, and count calls into the measure callback.

Covers plan items 5 (reusing a tree across frames), 8 (measure memoization) and 9 (LTO).
"""

from collections import Counter

from workloads import (
    DASHBOARD_AVAILABLE,
    best_of,
    build_dashboard,
    format_time,
    measure_text,
    report,
)

import waxy


def new_tree_frame() -> None:
    """Build a new tree and compute it, as counterweight does every frame today."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)


def new_tree_frame_without_measure() -> None:
    """Build a new tree and compute it with no measure callback."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE)


def measure_calls() -> list[tuple[str, str]]:
    """Count calls into the measure callback for a new tree and for a reused one."""
    calls: list[tuple[waxy.KnownSize, waxy.AvailableSize, str]] = []

    def counting_measure(
        known: waxy.KnownSize, available: waxy.AvailableSize, text: str
    ) -> waxy.Size:
        calls.append((known, available, text))
        return measure_text(known, available, text)

    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, leaves = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, counting_measure)
    new_tree_calls = list(calls)

    calls.clear()
    tree.set_node_context(leaves[0], "Changed text")
    tree.compute_layout(root, DASHBOARD_AVAILABLE, counting_measure)
    reuse_calls = len(calls)

    per_leaf = Counter(text for _, _, text in new_tree_calls)
    distinct_per_leaf = Counter(text for _, _, text in set(new_tree_calls))
    leaf = next(iter(per_leaf))
    return [
        ("measure calls, new tree", str(len(new_tree_calls))),
        ("measure calls, reused tree with one leaf changed", str(reuse_calls)),
        ("measure calls for one leaf, new tree", str(per_leaf[leaf])),
        ("distinct measure inputs for that leaf", str(distinct_per_leaf[leaf])),
    ]


def reuse_frame_time() -> float:
    """Time recomputing a reused tree after changing one leaf's context."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, leaves = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)
    texts = ["Changed text", "Other text"]
    frame = 0

    def reuse_frame() -> None:
        nonlocal frame
        frame += 1
        tree.set_node_context(leaves[0], texts[frame % 2])
        tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)

    return best_of(reuse_frame, 2_000)


def read_back_times() -> tuple[float, float]:
    """Time reading every node's layout and absolute position, in Python and with one call."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    tree.compute_layout(root, DASHBOARD_AVAILABLE, measure_text)

    def recurse(
        node: waxy.NodeId,
        origin: waxy.Point,
        out: list[tuple[waxy.NodeId, waxy.Point, waxy.Layout]],
    ) -> None:
        layout = tree.layout(node)
        position = origin + layout.location
        out.append((node, position, layout))
        for child in tree.children(node):
            recurse(child, position, out)

    def python_recursion() -> None:
        recurse(root, waxy.Point(), [])

    return (
        best_of(python_recursion, 5_000),
        best_of(lambda: tree.absolute_layouts(root), 5_000),
    )


def children_time() -> float:
    """Time `tree.children(node)` on a card."""
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root, _ = build_dashboard(tree)
    row = tree.children(root)[0]
    return best_of(lambda: tree.children(row), 500_000)


if __name__ == "__main__":
    report(
        [
            ("new tree, build and compute", format_time(best_of(new_tree_frame, 2_000))),
            (
                "new tree, build and compute, no measure",
                format_time(best_of(new_tree_frame_without_measure, 2_000)),
            ),
            ("reused tree, change one leaf, compute", format_time(reuse_frame_time())),
            ("tree.children(node)", format_time(children_time())),
            *zip(
                ["read back, Python recursion", "read back, absolute_layouts"],
                map(format_time, read_back_times()),
                strict=True,
            ),
            *measure_calls(),
        ]
    )
