"""
Property tests of `absolute_layouts` and `hoisted_children` over generated trees.

The oracle works out containing blocks from styles alone, by CSS's rules, without reading
taffy's hoisted lists. An `Absolute` box's containing block is its nearest positioned ancestor
(any `position` but `Static`), or the initial containing block if there is none. A `Fixed`
box's is the initial containing block. Every other box's is its parent. The layout root stands
in for the initial containing block. CSS has other ways to make a containing block (`contain`,
`transform`, ...), and taffy implements none of them, so the generated styles leave out
`contain` rather than have the oracle copy taffy's gap.

Positions are the sums of `Layout.location` along that chain, since each `location` is
relative to its containing block. Rounded positions are the unrounded sums rounded half up,
summed in f32 top-down; that part is taffy's own rounding convention (taffy#1189), not CSS.
"""

from __future__ import annotations

import math
import struct
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    Bundle,
    MultipleResults,
    RuleBasedStateMachine,
    consumes,
    initialize,
    invariant,
    multiple,
    rule,
)

import waxy

style_from_keywords: Callable[..., waxy.Style] = waxy.Style


def members[T](enum: type[T]) -> list[T]:
    """Every member of a waxy enum (pyo3 enums aren't iterable)."""
    return [getattr(enum, name) for name in dir(enum) if name[0].isupper()]


def to_f32(value: float) -> float:
    """Round a Python float to the nearest f32, to redo taffy's f32 arithmetic exactly."""
    return float(struct.unpack("f", struct.pack("f", value))[0])


def round_like_taffy(value: float) -> float:
    """Taffy's pixel rounding: half up, so round(-0.5) is 0, unlike Rust's `f32::round`."""
    return float(math.floor(value + 0.5))


# Fractional f32 offsets, so rounding has something to do; small enough that integer sums of
# rounded values stay exact in f32.
offsets = st.floats(min_value=-40, max_value=40, width=32)
extents = st.floats(min_value=0, max_value=60, width=32)
lengths = extents.map(waxy.Length)
percents = st.floats(min_value=0, max_value=1, width=32).map(waxy.Percent)
length_percentage_auto = st.one_of(offsets.map(waxy.Length), percents, st.just(waxy.AUTO))
dimensions = st.one_of(lengths, percents, st.just(waxy.AUTO))
tracks = st.lists(
    st.one_of(lengths, st.integers(1, 3).map(waxy.Fraction), st.just(waxy.AUTO)),
    min_size=1,
    max_size=3,
)
placements = st.builds(
    waxy.GridPlacement,
    st.one_of(st.none(), st.integers(1, 3).map(waxy.GridLine)),
    st.one_of(st.none(), st.integers(1, 2).map(waxy.GridSpan)),
)

STYLE_FIELDS: dict[str, st.SearchStrategy[object]] = {
    "display": st.sampled_from(members(waxy.Display)),
    "position": st.sampled_from(members(waxy.Position)),
    "direction": st.sampled_from(members(waxy.Direction)),
    "overflow_x": st.sampled_from(members(waxy.Overflow)),
    "float": st.sampled_from(members(waxy.Float)),
    "flex_direction": st.sampled_from(members(waxy.FlexDirection)),
    "flex_wrap": st.sampled_from(members(waxy.FlexWrap)),
    "align_items": st.sampled_from(members(waxy.AlignItems)),
    "justify_items": st.sampled_from(members(waxy.AlignItems)),
    "align_self": st.sampled_from(members(waxy.AlignItems)),
    "justify_self": st.sampled_from(members(waxy.AlignItems)),
    "align_content": st.sampled_from(members(waxy.AlignContent)),
    "justify_content": st.sampled_from(members(waxy.AlignContent)),
    "inset_left": length_percentage_auto,
    "inset_right": length_percentage_auto,
    "inset_top": length_percentage_auto,
    "inset_bottom": length_percentage_auto,
    "margin_left": length_percentage_auto,
    "margin_top": length_percentage_auto,
    "padding_left": lengths,
    "padding_top": lengths,
    "border_left": lengths,
    "border_top": lengths,
    "size_width": dimensions,
    "size_height": dimensions,
    "gap_width": lengths,
    "grid_template_columns": tracks,
    "grid_template_rows": tracks,
    "grid_row": placements,
    "grid_column": placements,
}

styles = (
    st.dictionaries(
        st.sampled_from(sorted(STYLE_FIELDS)), st.just(None), max_size=len(STYLE_FIELDS)
    )
    .flatmap(lambda chosen: st.fixed_dictionaries({name: STYLE_FIELDS[name] for name in chosen}))
    .map(lambda keywords: style_from_keywords(**keywords))
)

# For edit sequences: every node is offset from where its location is measured from, and most
# make or use containing blocks, so moving a box between containing blocks moves it on screen.
# The full style space is left to the single-layout property, where it costs no search depth.
edit_styles = st.builds(
    waxy.Style,
    display=st.sampled_from([waxy.Display.Flex] * 3 + [waxy.Display.Block, waxy.Display.Nil]),
    position=st.sampled_from(
        [
            waxy.Position.Absolute,
            waxy.Position.Absolute,
            waxy.Position.Relative,
            waxy.Position.Relative,
            waxy.Position.Fixed,
            waxy.Position.Static,
            waxy.Position.Sticky,
        ]
    ),
    margin_left=st.integers(1, 9).map(waxy.Length),
    margin_top=st.integers(1, 9).map(waxy.Length),
    inset_left=offsets.map(waxy.Length),
    inset_top=offsets.map(waxy.Length),
    size_width=extents.map(waxy.Length),
    size_height=extents.map(waxy.Length),
)

available_sizes = st.one_of(
    st.none(),
    st.builds(
        waxy.AvailableSize,
        st.one_of(
            extents.map(waxy.Definite), st.just(waxy.MaxContent()), st.just(waxy.MinContent())
        ),
        st.one_of(
            extents.map(waxy.Definite), st.just(waxy.MaxContent()), st.just(waxy.MinContent())
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class Spec:
    """A tree to build: a node's style and its children's specs."""

    style: waxy.Style
    children: tuple[Spec, ...]


specs: st.SearchStrategy[Spec] = st.recursive(
    st.builds(Spec, styles, st.just(())),
    lambda inner: st.builds(Spec, styles, st.lists(inner, max_size=4).map(tuple)),
    max_leaves=16,
)


# Trees for edit sequences to start from, small enough that edits reshape them.
edit_specs: st.SearchStrategy[Spec] = st.recursive(
    st.builds(Spec, edit_styles, st.just(())),
    lambda inner: st.builds(Spec, edit_styles, st.lists(inner, max_size=3).map(tuple)),
    max_leaves=10,
)


def build(tree: waxy.TaffyTree[object], spec: Spec) -> waxy.NodeId:
    return tree.new_with_children(spec.style, [build(tree, child) for child in spec.children])


def is_hidden(tree: waxy.TaffyTree[object], node: waxy.NodeId) -> bool:
    return tree.style(node).display == waxy.Display.Nil


def visible_pre_order(tree: waxy.TaffyTree[object], root: waxy.NodeId) -> Iterator[waxy.NodeId]:
    """The nodes `absolute_layouts(root)` reports, in the order it reports them."""
    if is_hidden(tree, root):
        return
    yield root
    for child in tree.children(root):
        yield from visible_pre_order(tree, child)


def containing_block(
    tree: waxy.TaffyTree[object], node: waxy.NodeId, layout_root: waxy.NodeId
) -> waxy.NodeId:
    """What `node`'s location is relative to, from styles alone."""
    parent = tree.parent(node)
    assert parent is not None, "the layout root has no containing block"
    match tree.style(node).position:
        case waxy.Position.Fixed:
            return layout_root
        case waxy.Position.Absolute:
            ancestor: waxy.NodeId | None = parent
            while ancestor != layout_root:
                assert ancestor is not None, "the node isn't under the layout root"
                if tree.style(ancestor).position != waxy.Position.Static:
                    return ancestor
                ancestor = tree.parent(ancestor)
            return layout_root
        case _:
            return parent


def expected_hoisted(
    tree: waxy.TaffyTree[object], layout_root: waxy.NodeId
) -> dict[waxy.NodeId, Counter[waxy.NodeId]]:
    """Each visible node's out-of-flow boxes, the nodes it's the containing block for."""
    hoisted: dict[waxy.NodeId, Counter[waxy.NodeId]] = {}
    for node in visible_pre_order(tree, layout_root):
        hoisted.setdefault(node, Counter())
        if node == layout_root:
            continue
        if tree.style(node).position in (waxy.Position.Absolute, waxy.Position.Fixed):
            hoisted.setdefault(containing_block(tree, node, layout_root), Counter())[node] += 1
    return hoisted


def chain_sums(
    tree: waxy.TaffyTree[object],
    layout_root: waxy.NodeId,
    location: Callable[[waxy.NodeId], waxy.Point],
) -> dict[waxy.NodeId, tuple[float, float]]:
    """Each visible node's `location` summed in f32 along its chain of containing blocks."""
    sums: dict[waxy.NodeId, tuple[float, float]] = {}
    for node in visible_pre_order(tree, layout_root):
        offset = location(node)
        if node == layout_root:
            sums[node] = (offset.x, offset.y)
            continue
        x, y = sums[containing_block(tree, node, layout_root)]
        sums[node] = (to_f32(x + offset.x), to_f32(y + offset.y))
    return sums


def positions(
    tree: waxy.TaffyTree[object], root: waxy.NodeId
) -> list[tuple[waxy.NodeId, tuple[float, float]]]:
    return [(node, (point.x, point.y)) for node, point, _ in tree.absolute_layouts(root)]


def assert_matches_oracle(
    tree: waxy.TaffyTree[object], layout_root: waxy.NodeId, is_rounded: bool, is_rounding: bool
) -> None:
    """
    Check `absolute_layouts` and `hoisted_children` for a tree laid out from `layout_root`.

    `is_rounded` is whether rounding was enabled for that `compute_layout`, and `is_rounding`
    whether it is now: toggling it changes what `layout` returns without a new layout.
    """
    reported = positions(tree, layout_root)
    assert [node for node, _ in reported] == list(visible_pre_order(tree, layout_root))

    # Whatever the current setting, positions sum the locations `layout` returns.
    assert dict(reported) == chain_sums(tree, layout_root, lambda node: tree.layout(node).location)
    for node, _, layout in tree.absolute_layouts(layout_root):
        assert layout == tree.layout(node)

    # With the setting the layout was computed under, rounded positions are the rounded
    # unrounded sums, and rounded sizes end where the unrounded box does.
    if is_rounded == is_rounding:
        unrounded = chain_sums(tree, layout_root, lambda node: tree.unrounded_layout(node).location)
        for node, (x, y) in reported:
            left, top = unrounded[node]
            if not is_rounded:
                assert (x, y) == (left, top)
                continue
            size = tree.unrounded_layout(node).size
            assert (x, y) == (round_like_taffy(left), round_like_taffy(top))
            assert x + tree.layout(node).size.width == round_like_taffy(to_f32(left + size.width))
            assert y + tree.layout(node).size.height == round_like_taffy(to_f32(top + size.height))

    for node, expected in expected_hoisted(tree, layout_root).items():
        assert Counter(tree.hoisted_children(node)) == expected, node

    # Every subtree's list is the matching run of the whole tree's.
    whole = tree.absolute_layouts(layout_root)
    for index, (node, _, _) in enumerate(whole):
        subtree = tree.absolute_layouts(node)
        assert subtree == whole[index : index + len(subtree)]


@settings(max_examples=300, deadline=None)
@given(spec=specs, available=available_sizes, is_rounded=st.booleans())
def test_absolute_layouts_match_containing_block_model(
    spec: Spec, available: waxy.AvailableSize | None, is_rounded: bool
) -> None:
    tree: waxy.TaffyTree[object] = waxy.TaffyTree()
    if not is_rounded:
        tree.disable_rounding()
    root = build(tree, spec)
    tree.compute_layout(root, available)
    assert_matches_oracle(tree, root, is_rounded, is_rounded)


class EditedTree(RuleBasedStateMachine):
    """
    A tree edited between layouts, checked against the oracle and against a fresh rebuild.

    taffy keeps state across layouts (caches, hoisted lists) that edits must invalidate, so a
    tree reached by edits must lay out exactly as the same tree built from scratch. Edits also
    reach detached subtrees, which carry their stale state back when reattached.
    """

    nodes = Bundle("nodes")
    root: waxy.NodeId

    def __init__(self) -> None:
        super().__init__()
        self.tree: waxy.TaffyTree[object] = waxy.TaffyTree()
        self.is_rounding = True
        self.layout: tuple[bool, waxy.AvailableSize | None] | None = None
        """Whether the last layout was rounded, and its available space; None once edited."""
        self.last_hoisted: dict[waxy.NodeId, list[waxy.NodeId]] = {}
        """Each node's hoisted list from the last layout that ran its out-of-flow pass."""

    @initialize(target=nodes, spec=edit_specs)
    def build_tree(self, spec: Spec) -> MultipleResults[waxy.NodeId]:
        self.root = build(self.tree, spec)
        if is_hidden(self.tree, self.root):
            self.tree.set_style(self.root, spec.style | waxy.Style(display=waxy.Display.Flex))
        return multiple(*self.subtree(self.root))

    def subtree(self, node: waxy.NodeId) -> Iterator[waxy.NodeId]:
        yield node
        for child in self.tree.children(node):
            yield from self.subtree(child)

    def insert(self, parent: waxy.NodeId, index: int, node: waxy.NodeId) -> None:
        self.tree.insert_child_at_index(parent, min(index, self.tree.child_count(parent)), node)
        self.layout = None

    @rule(target=nodes, parent=nodes, style=edit_styles, index=st.integers(0, 4))
    def add_leaf(self, parent: waxy.NodeId, style: waxy.Style, index: int) -> waxy.NodeId:
        node = self.tree.new_leaf(style)
        self.insert(parent, index, node)
        return node

    @rule(node=nodes, style=edit_styles)
    def set_style(self, node: waxy.NodeId, style: waxy.Style) -> None:
        # A hidden root leaves nothing to check.
        if node == self.root and style.display == waxy.Display.Nil:
            return
        self.tree.set_style(node, style)
        self.layout = None

    @rule(node=nodes, position=st.sampled_from(members(waxy.Position)))
    def set_position(self, node: waxy.NodeId, position: waxy.Position) -> None:
        """Change only `position`, so containing blocks move without the rest of the layout."""
        self.tree.set_style(node, self.tree.style(node) | waxy.Style(position=position))
        self.layout = None

    @rule(node=nodes)
    def detach(self, node: waxy.NodeId) -> None:
        if (parent := self.tree.parent(node)) is not None:
            self.tree.remove_child(parent, node)
            self.layout = None

    @rule(target=nodes, node=consumes(nodes))
    def remove(self, node: waxy.NodeId) -> MultipleResults[waxy.NodeId]:
        """Delete `node`, as closing a popup does, leaving its children detached."""
        if node == self.root:
            return multiple(node)
        self.tree.remove(node)
        self.last_hoisted.pop(node, None)
        self.layout = None
        return multiple()

    @rule(node=nodes, parent=nodes, index=st.integers(0, 4))
    def move(self, node: waxy.NodeId, parent: waxy.NodeId, index: int) -> None:
        if node == self.root or parent in self.subtree(node):
            return
        if (old_parent := self.tree.parent(node)) is not None:
            self.tree.remove_child(old_parent, node)
        self.insert(parent, index, node)

    @rule(is_rounding=st.booleans())
    def set_rounding(self, is_rounding: bool) -> None:
        if is_rounding:
            self.tree.enable_rounding()
        else:
            self.tree.disable_rounding()
        self.is_rounding = is_rounding

    def skips_out_of_flow_pass(self) -> Iterator[waxy.NodeId]:
        """The nodes the next layout gives no out-of-flow pass: leaves, and hidden subtrees."""
        pending = [(self.root, False)]
        while pending:
            node, is_in_hidden_subtree = pending.pop()
            is_in_hidden_subtree = is_in_hidden_subtree or is_hidden(self.tree, node)
            children = self.tree.children(node)
            if is_in_hidden_subtree or not children:
                yield node
            pending.extend((child, is_in_hidden_subtree) for child in children)

    def has_stale_hoisted_list(self) -> bool:
        """
        Whether taffy will round from a stale hoisted list, which it gets wrong.

        TODO(taffy#1354): drop this once taffy clears the hoisted list of a node that skips the
        out-of-flow pass. Its rounding pass walks every node's list, so a stale one rounds a box
        again from the wrong node, panics naming a deleted box, or, naming an ancestor, recurses
        until the stack overflows. See `test_rounding_ignores_hoisted_list_of_node_left_a_leaf`,
        `test_compute_layout_survives_deleting_box_of_emptied_or_hidden_container` and
        `test_compute_layout_survives_nesting_a_containing_block_in_its_box`.
        """
        return any(self.last_hoisted.get(node) for node in self.skips_out_of_flow_pass())

    @rule(available=available_sizes)
    def compute_layout(self, available: waxy.AvailableSize | None) -> None:
        if self.is_rounding and self.has_stale_hoisted_list():
            return
        skipped = set(self.skips_out_of_flow_pass())
        self.tree.compute_layout(self.root, available)
        self.layout = (self.is_rounding, available)
        for node in self.subtree(self.root):
            if node not in skipped:
                self.last_hoisted[node] = self.tree.hoisted_children(node)

    def rebuild(self, fresh: waxy.TaffyTree[object], node: waxy.NodeId) -> waxy.NodeId:
        children = [self.rebuild(fresh, child) for child in self.tree.children(node)]
        return fresh.new_with_children(self.tree.style(node), children)

    @invariant()
    def matches_oracle(self) -> None:
        if self.layout is None:
            return
        is_rounded, _ = self.layout
        assert_matches_oracle(self.tree, self.root, is_rounded, self.is_rounding)

    @invariant()
    def matches_fresh_tree(self) -> None:
        if self.layout is None:
            return
        is_rounded, available = self.layout
        # Enabling rounding after an unrounded layout makes `layout` return whatever rounded
        # layout taffy last stored, which depends on history by design.
        if is_rounded != self.is_rounding:
            return
        fresh: waxy.TaffyTree[object] = waxy.TaffyTree()
        if not is_rounded:
            fresh.disable_rounding()
        fresh_root = self.rebuild(fresh, self.root)
        fresh.compute_layout(fresh_root, available)
        edited = [(point, layout) for _, point, layout in self.tree.absolute_layouts(self.root)]
        rebuilt = [(point, layout) for _, point, layout in fresh.absolute_layouts(fresh_root)]
        assert edited == rebuilt


EditedTree.TestCase.settings = settings(max_examples=200, stateful_step_count=40, deadline=None)
test_edited_tree_lays_out_like_a_fresh_one = EditedTree.TestCase
