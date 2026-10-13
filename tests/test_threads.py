# `sys.UnraisableHookArgs` exists only in typeshed, so the annotations naming it mustn't be
# evaluated, which Python 3.13 does eagerly without this.
from __future__ import annotations

import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import pytest

import waxy


@pytest.fixture
def unraisables(monkeypatch: pytest.MonkeyPatch) -> list[sys.UnraisableHookArgs]:
    """Every exception raised where Python can't propagate it, such as in a destructor."""
    caught: list[sys.UnraisableHookArgs] = []
    monkeypatch.setattr(sys, "unraisablehook", caught.append)
    return caught


def run_on_another_thread[T](function: Callable[[], T]) -> T:
    """Run `function` on a fresh thread, re-raising anything it raises."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(function).result()


def tree_with_nodes() -> waxy.TaffyTree[object]:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    child = tree.new_leaf_with_context(waxy.Style(size_width=waxy.Length(30.0)), "child")
    tree.new_with_children(waxy.Style(padding_left=waxy.Length(5.0)), [child])
    return tree


@pytest.mark.parametrize(
    "build",
    [
        waxy.Style,
        lambda: waxy.Style(size_width=waxy.Length(40.0), flex_grow=2.0),
        waxy.TaffyTree,
        tree_with_nodes,
    ],
)
def test_dropping_on_another_thread_raises_nothing(
    build: Callable[[], object], unraisables: list[sys.UnraisableHookArgs]
) -> None:
    # Only the list holds the object, so clearing it on the other thread drops it there.
    holder = [build()]

    run_on_another_thread(holder.clear)

    assert unraisables == []


def test_tree_built_on_one_thread_computes_layout_on_another() -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    node = tree.new_leaf(waxy.Style(size_width=waxy.Length(70.0), size_height=waxy.Length(20.0)))

    run_on_another_thread(lambda: tree.compute_layout(node))

    assert tree.layout(node).size == waxy.Size(70.0, 20.0)


def test_style_hashes_the_same_on_another_thread() -> None:
    style = waxy.Style(size_width=waxy.Length(60.0), flex_shrink=3.0)

    assert run_on_another_thread(lambda: hash(style)) == hash(style)
