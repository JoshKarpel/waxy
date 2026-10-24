import textwrap
import weakref
from collections.abc import Callable
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

import waxy

# --- KnownSize ---


def test_known_size_construction() -> None:
    kd = waxy.KnownSize(width=100.0, height=None)
    assert kd.width == 100.0
    assert kd.height is None


def test_known_size_defaults() -> None:
    kd = waxy.KnownSize()
    assert kd.width is None
    assert kd.height is None


def test_known_size_unpacking() -> None:
    kd = waxy.KnownSize(width=50.0, height=75.0)
    w, h = kd
    assert w == 50.0
    assert h == 75.0


def test_known_size_repr() -> None:
    kd = waxy.KnownSize(width=10.0, height=None)
    assert "10" in repr(kd)
    assert "None" in repr(kd)


def test_known_size_eq() -> None:
    assert waxy.KnownSize(width=1.0) == waxy.KnownSize(width=1.0)
    assert waxy.KnownSize(width=1.0) != waxy.KnownSize(width=2.0)


# --- AvailableSize ---


def test_available_size_construction() -> None:
    ad = waxy.AvailableSize(
        width=waxy.Definite(100.0),
        height=waxy.MaxContent(),
    )
    assert isinstance(ad.width, waxy.Definite)
    assert ad.width.value == 100.0
    assert isinstance(ad.height, waxy.MaxContent)


def test_available_size_unpacking() -> None:
    ad = waxy.AvailableSize(
        width=waxy.Definite(200.0),
        height=waxy.MinContent(),
    )
    w, h = ad
    assert isinstance(w, waxy.Definite)
    assert w.value == 200.0
    assert isinstance(h, waxy.MinContent)


def test_available_size_repr() -> None:
    ad = waxy.AvailableSize(
        width=waxy.Definite(100.0),
        height=waxy.MaxContent(),
    )
    r = repr(ad)
    assert "AvailableSize" in r
    assert "100" in r


def test_available_size_eq() -> None:
    a = waxy.AvailableSize(
        width=waxy.Definite(100.0),
        height=waxy.MaxContent(),
    )
    b = waxy.AvailableSize(
        width=waxy.Definite(100.0),
        height=waxy.MaxContent(),
    )
    assert a == b


# --- Definite / MinContent / MaxContent ---


def test_definite_value() -> None:
    assert waxy.Definite(42.0).value == 42.0


def test_min_content_identity() -> None:
    assert isinstance(waxy.MinContent(), waxy.MinContent)
    assert not isinstance(waxy.MaxContent(), waxy.MinContent)
    assert not isinstance(waxy.Definite(100.0), waxy.MinContent)


def test_max_content_identity() -> None:
    assert isinstance(waxy.MaxContent(), waxy.MaxContent)
    assert not isinstance(waxy.MinContent(), waxy.MaxContent)
    assert not isinstance(waxy.Definite(100.0), waxy.MaxContent)


# --- Node context ---


@dataclass(frozen=True, slots=True)
class FixedContent:
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class TextContent:
    text: str


def test_new_leaf_with_context() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf_with_context(waxy.Style(), TextContent("hello"))
    assert tree.total_node_count() == 1
    assert isinstance(node, waxy.NodeId)


def test_get_node_context() -> None:
    tree = waxy.TaffyTree[TextContent]()
    ctx = TextContent("hello")
    node = tree.new_leaf_with_context(waxy.Style(), ctx)
    result = tree.get_node_context(node)
    assert result == ctx


def test_get_node_context_returns_none_for_no_context() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf(waxy.Style())
    assert tree.get_node_context(node) is None


def test_set_node_context() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf_with_context(waxy.Style(), TextContent("hello"))
    tree.set_node_context(node, TextContent("world"))
    assert tree.get_node_context(node) == TextContent("world")


def test_set_node_context_clear() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf_with_context(waxy.Style(), TextContent("hello"))
    tree.set_node_context(node, None)
    assert tree.get_node_context(node) is None


class Referent:
    """A context that can be weakly referenced, to observe when the tree releases it."""


@pytest.mark.parametrize(
    "release",
    [
        lambda tree, node: tree.remove(node),
        lambda tree, node: tree.clear(),
    ],
    ids=["remove", "clear"],
)
def test_removing_node_releases_its_context(
    release: Callable[[waxy.TaffyTree[Referent], waxy.NodeId], object],
) -> None:
    tree = waxy.TaffyTree[Referent]()
    context = Referent()
    alive = weakref.ref(context)
    node = tree.new_leaf_with_context(waxy.Style(), context)
    del context
    release(tree, node)
    assert alive() is None


# --- Measure functions ---


def test_compute_layout_with_fixed_measure() -> None:
    tree = waxy.TaffyTree[FixedContent]()
    node = tree.new_leaf_with_context(
        waxy.Style(),
        FixedContent(width=200.0, height=100.0),
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: FixedContent,
    ) -> waxy.Size:
        return waxy.Size(context.width, context.height)

    tree.compute_layout(root, measure=measure)
    layout = tree.layout(node)
    assert layout.size.width == 200.0
    assert layout.size.height == 100.0


def test_compute_layout_text_wrapping() -> None:
    tree = waxy.TaffyTree[TextContent]()
    # Give the text node an explicit width so it wraps
    text_node = tree.new_leaf_with_context(
        waxy.Style(size_width=waxy.Length(100)),
        TextContent("Hello world, this is some text"),
    )
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Flex),
        [text_node],
    )

    char_width = 8.0
    char_height = 16.0

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: TextContent,
    ) -> waxy.Size:
        kw, _ = known
        avail_w, _ = available
        text = context.text

        if kw is not None:
            inline_size = kw
        elif isinstance(avail_w, waxy.Definite):
            inline_size = avail_w.value
        else:
            inline_size = len(text) * char_width

        chars_per_line = max(1, int(inline_size / char_width))
        lines = textwrap.wrap(text, width=chars_per_line)
        line_count = max(1, len(lines))

        return waxy.Size(inline_size, line_count * char_height)

    tree.compute_layout(root, measure=measure)
    layout = tree.layout(text_node)
    # Text wraps at 100px width — known provides kw=100
    assert layout.size.width == 100.0
    assert layout.size.height > char_height  # Multiple lines


def test_measure_receives_known_dimensions_from_style() -> None:
    tree = waxy.TaffyTree[str]()
    # Node with explicit width in style
    node = tree.new_leaf_with_context(
        waxy.Style(size_width=waxy.Length(150)),
        "test",
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    received_kd: list[waxy.KnownSize] = []

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: str,
    ) -> waxy.Size:
        received_kd.append(known)
        kw, kh = known
        w = kw if kw is not None else 50.0
        h = kh if kh is not None else 30.0
        return waxy.Size(w, h)

    tree.compute_layout(root, measure=measure)
    # At least one call should have known width = 150
    assert any(kd.width == 150.0 for kd in received_kd)


def test_measure_not_called_for_nodes_without_context() -> None:
    tree = waxy.TaffyTree[FixedContent]()

    # One node with context, one without
    node_with_ctx = tree.new_leaf_with_context(
        waxy.Style(),
        FixedContent(width=50.0, height=30.0),
    )
    node_without_ctx = tree.new_leaf(waxy.Style())

    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Flex),
        [node_with_ctx, node_without_ctx],
    )

    mock_measure = MagicMock(side_effect=lambda kd, avail, ctx: waxy.Size(ctx.width, ctx.height))

    tree.compute_layout(root, measure=mock_measure)

    # The measure function should have been called at least once
    assert mock_measure.call_count >= 1

    # The measure function should only have been called for node_with_ctx
    for call in mock_measure.call_args_list:
        # 3rd arg (index 2) is context — should never be None
        assert call[0][2] is not None

    # node_without_ctx should get zero intrinsic width (height may stretch from flex)
    layout = tree.layout(node_without_ctx)
    assert layout.size.width == 0.0


def test_measure_error_propagation() -> None:
    tree = waxy.TaffyTree[str]()
    node = tree.new_leaf_with_context(waxy.Style(), "test")
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def bad_measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: str,
    ) -> waxy.Size:
        msg = "measure failed!"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="measure failed!"):
        tree.compute_layout(root, measure=bad_measure)


def test_layout_after_measure_error_measures_again() -> None:
    tree = waxy.TaffyTree[str]()
    failing = tree.new_leaf_with_context(waxy.Style(), "failing")
    after_failure = tree.new_leaf_with_context(waxy.Style(), "after_failure")
    root = tree.new_with_children(waxy.Style(), [failing, after_failure])

    def bad_measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: str,
    ) -> waxy.Size:
        if context == "failing":
            msg = "measure failed!"
            raise ValueError(msg)
        return waxy.Size(5, 5)

    with pytest.raises(ValueError, match="measure failed!"):
        tree.compute_layout(root, measure=bad_measure)

    tree.compute_layout(root, measure=lambda known, available, context: waxy.Size(7, 3))

    assert tree.layout(failing).size == waxy.Size(7, 3)
    assert tree.layout(after_failure).size == waxy.Size(7, 3)
    assert tree.layout(root).size == waxy.Size(14, 3)


def test_compute_layout_with_available_space_param() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf_with_context(
        waxy.Style(),
        TextContent("Some text"),
    )
    # Give the root an explicit size so it fills the viewport
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Flex, size_width=waxy.Length(800)),
        [node],
    )

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: TextContent,
    ) -> waxy.Size:
        kw, _ = known
        w = kw if kw is not None else len(context.text) * 8.0
        return waxy.Size(w, 16.0)

    viewport = waxy.AvailableSize(
        width=waxy.Definite(800.0),
        height=waxy.Definite(600.0),
    )
    tree.compute_layout(root, measure=measure, available=viewport)

    layout = tree.layout(root)
    assert layout.size.width == 800.0


def test_measure_with_max_content_available_space() -> None:
    """When available space is max-content, the measure function should report full content size."""
    tree = waxy.TaffyTree[TextContent]()
    text_node = tree.new_leaf_with_context(
        waxy.Style(),
        TextContent("Hello world"),
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [text_node])

    char_width = 8.0
    char_height = 16.0

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: TextContent,
    ) -> waxy.Size:
        kw, _ = known
        avail_w, _ = available

        if kw is not None:
            return waxy.Size(kw, char_height)

        # Max-content: report full single-line width
        if not isinstance(avail_w, waxy.Definite):
            return waxy.Size(len(context.text) * char_width, char_height)

        # Definite: use the available width
        return waxy.Size(avail_w.value, char_height)

    # Default available is max-content — node should get full single-line width
    tree.compute_layout(root, measure=measure)
    layout = tree.layout(text_node)
    assert layout.size.width == len("Hello world") * char_width  # 88.0
    assert layout.size.height == char_height


def test_measure_with_min_content_available_space() -> None:
    """When available space is min-content, the measure function should report minimum size."""
    tree = waxy.TaffyTree[TextContent]()
    text_node = tree.new_leaf_with_context(
        waxy.Style(),
        TextContent("Hello world"),
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [text_node])

    char_width = 8.0
    char_height = 16.0

    def measure(
        known: waxy.KnownSize,
        available: waxy.AvailableSize,
        context: TextContent,
    ) -> waxy.Size:
        kw, _ = known
        avail_w, _ = available

        if kw is not None:
            return waxy.Size(kw, char_height)

        if isinstance(avail_w, waxy.Definite):
            return waxy.Size(avail_w.value, char_height)

        text = context.text
        if isinstance(avail_w, waxy.MinContent):
            # Min-content: width of the longest word
            longest_word = max(text.split(), key=len)
            return waxy.Size(len(longest_word) * char_width, char_height)

        # Max-content: full single-line width
        return waxy.Size(len(text) * char_width, char_height)

    # Use min_content available space
    viewport = waxy.AvailableSize(
        width=waxy.MinContent(),
        height=waxy.MinContent(),
    )
    tree.compute_layout(root, measure=measure, available=viewport)
    layout = tree.layout(text_node)
    # "world" is the longest word (5 chars), so min-content width = 40.0
    assert layout.size.width == len("world") * char_width  # 40.0
    assert layout.size.height == char_height


def test_compute_layout_without_measure_still_works() -> None:
    """Existing behavior: leaf nodes without measure get zero intrinsic size."""
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Length(100.0),
        size_height=waxy.Length(50.0),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(node)
    layout = tree.layout(node)
    assert layout.size.width == 100.0
    assert layout.size.height == 50.0


def test_measured_leaf_size_includes_its_padding_and_border() -> None:
    def measure(known: waxy.KnownSize, available: waxy.AvailableSize, context: str) -> waxy.Size:
        return waxy.Size(40.0, 15.0)

    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    leaf = tree.new_leaf_with_context(
        waxy.Style(
            padding_left=waxy.Length(3.0),
            padding_right=waxy.Length(5.0),
            border_top=waxy.Length(2.0),
            min_size_height=waxy.Length(30.0),
        ),
        "text",
    )
    tree.compute_layout(leaf, measure=measure)
    assert tree.layout(leaf).size == waxy.Size(48.0, 30.0)


def build_cards(tree: waxy.TaffyTree[str], texts: list[str]) -> waxy.NodeId:
    """A row of bordered cards, each a column holding one text leaf, which taffy measures often."""
    card_style = waxy.Style(
        flex_direction=waxy.FlexDirection.Column,
        flex_grow=1,
        border_left=waxy.Length(1),
        border_right=waxy.Length(1),
    )
    cards = [
        tree.new_with_children(card_style, [tree.new_leaf_with_context(waxy.Style(), text)])
        for text in texts
    ]
    return tree.new_with_children(waxy.Style(size_width=waxy.Length(30)), cards)


def measure_text(known: waxy.KnownSize, available: waxy.AvailableSize, text: str) -> waxy.Size:
    """One cell per character, wrapped to the offered width."""
    match known.width, available.width:
        case float() as width, _:
            pass
        case None, waxy.Definite(value):
            width = min(float(len(text)), value)
        case _:
            width = float(len(text))
    return waxy.Size(width, float(-(-len(text) // max(int(width), 1))))


def test_measure_called_once_per_distinct_input_per_node() -> None:
    calls: list[tuple[waxy.KnownSize, waxy.AvailableSize, str]] = []

    def counting_measure(
        known: waxy.KnownSize, available: waxy.AvailableSize, text: str
    ) -> waxy.Size:
        calls.append((known, available, text))
        return measure_text(known, available, text)

    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    root = build_cards(tree, ["a longer piece of text", "short", "medium text"])
    tree.compute_layout(root, measure=counting_measure)

    assert len(calls) == len(set(calls))


def test_measure_memo_keeps_results_separate_per_node() -> None:
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    # The leaves sit in identical positions, so taffy asks both the same questions.
    narrow = tree.new_leaf_with_context(waxy.Style(), "ab")
    wide = tree.new_leaf_with_context(waxy.Style(), "abcdefgh")
    root = tree.new_with_children(
        waxy.Style(flex_direction=waxy.FlexDirection.Column, align_items=waxy.AlignItems.Start),
        [narrow, wide],
    )
    tree.compute_layout(root, measure=measure_text)

    assert tree.layout(narrow).size.width == 2
    assert tree.layout(wide).size.width == 8


def test_measure_memo_does_not_outlive_one_compute_layout_call() -> None:
    tree: waxy.TaffyTree[str] = waxy.TaffyTree()
    leaf = tree.new_leaf_with_context(waxy.Style(), "text")
    tree.compute_layout(leaf, measure=lambda known, available, text: waxy.Size(3, 1))

    tree.mark_dirty(leaf)
    tree.compute_layout(leaf, measure=lambda known, available, text: waxy.Size(7, 1))

    assert tree.layout(leaf).size.width == 7
