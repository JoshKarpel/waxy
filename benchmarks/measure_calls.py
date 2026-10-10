"""
Count calls into the measure callback while laying out the dashboard-shaped tree.

Times live in `suite.py`; this reports how often taffy asks for a measurement,
which bounds how much any per-call saving in waxy or in a callback can be worth.
"""

from collections import Counter

from workloads import DASHBOARD_AVAILABLE, build_dashboard, measure_text, report

import waxy


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


if __name__ == "__main__":
    report(measure_calls())
