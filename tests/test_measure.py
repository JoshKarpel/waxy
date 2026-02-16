import textwrap
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

import waxy

# --- KnownDimensions ---


def test_known_dimensions_construction() -> None:
    kd = waxy.KnownDimensions(width=100.0, height=None)
    assert kd.width == 100.0
    assert kd.height is None


def test_known_dimensions_defaults() -> None:
    kd = waxy.KnownDimensions()
    assert kd.width is None
    assert kd.height is None


def test_known_dimensions_unpacking() -> None:
    kd = waxy.KnownDimensions(width=50.0, height=75.0)
    w, h = kd
    assert w == 50.0
    assert h == 75.0


def test_known_dimensions_repr() -> None:
    kd = waxy.KnownDimensions(width=10.0, height=None)
    assert "10" in repr(kd)
    assert "None" in repr(kd)


def test_known_dimensions_eq() -> None:
    assert waxy.KnownDimensions(width=1.0) == waxy.KnownDimensions(width=1.0)
    assert waxy.KnownDimensions(width=1.0) != waxy.KnownDimensions(width=2.0)


# --- AvailableDimensions ---


def test_available_dimensions_construction() -> None:
    ad = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(100.0),
        height=waxy.AvailableSpace.max_content(),
    )
    assert ad.width.is_definite()
    assert ad.width.value() == 100.0
    assert not ad.height.is_definite()


def test_available_dimensions_unpacking() -> None:
    ad = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(200.0),
        height=waxy.AvailableSpace.min_content(),
    )
    w, h = ad
    assert w.is_definite()
    assert w.value() == 200.0
    assert not h.is_definite()


def test_available_dimensions_repr() -> None:
    ad = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(100.0),
        height=waxy.AvailableSpace.max_content(),
    )
    r = repr(ad)
    assert "AvailableDimensions" in r
    assert "100" in r


def test_available_dimensions_eq() -> None:
    a = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(100.0),
        height=waxy.AvailableSpace.max_content(),
    )
    b = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(100.0),
        height=waxy.AvailableSpace.max_content(),
    )
    assert a == b


# --- AvailableSpace.value() ---


def test_available_space_value_definite() -> None:
    assert waxy.AvailableSpace.definite(42.0).value() == 42.0


def test_available_space_value_none_for_non_definite() -> None:
    assert waxy.AvailableSpace.min_content().value() is None
    assert waxy.AvailableSpace.max_content().value() is None


def test_available_space_is_min_content() -> None:
    assert waxy.AvailableSpace.min_content().is_min_content()
    assert not waxy.AvailableSpace.max_content().is_min_content()
    assert not waxy.AvailableSpace.definite(100.0).is_min_content()


def test_available_space_is_max_content() -> None:
    assert waxy.AvailableSpace.max_content().is_max_content()
    assert not waxy.AvailableSpace.min_content().is_max_content()
    assert not waxy.AvailableSpace.definite(100.0).is_max_content()


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


# --- Measure functions ---


def test_compute_layout_with_fixed_measure() -> None:
    tree = waxy.TaffyTree[FixedContent]()
    node = tree.new_leaf_with_context(
        waxy.Style(),
        FixedContent(width=200.0, height=100.0),
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def measure(
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: FixedContent,
        style: waxy.Style,
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
        waxy.Style(size_width=waxy.length(100)),
        TextContent("Hello world, this is some text"),
    )
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Flex),
        [text_node],
    )

    char_width = 8.0
    char_height = 16.0

    def measure(
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: TextContent,
        style: waxy.Style,
    ) -> waxy.Size:
        kw, _ = known_dimensions
        avail_w, _ = available_space
        text = context.text

        if kw is not None:
            inline_size = kw
        elif avail_w.is_definite():
            inline_size = avail_w.value()  # type: ignore[assignment]
        else:
            inline_size = len(text) * char_width

        chars_per_line = max(1, int(inline_size / char_width))
        lines = textwrap.wrap(text, width=chars_per_line)
        line_count = max(1, len(lines))

        return waxy.Size(inline_size, line_count * char_height)

    tree.compute_layout(root, measure=measure)
    layout = tree.layout(text_node)
    # Text wraps at 100px width — known_dimensions provides kw=100
    assert layout.size.width == 100.0
    assert layout.size.height > char_height  # Multiple lines


def test_measure_receives_known_dimensions_from_style() -> None:
    tree = waxy.TaffyTree[str]()
    # Node with explicit width in style
    node = tree.new_leaf_with_context(
        waxy.Style(size_width=waxy.length(150)),
        "test",
    )
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    received_kd: list[waxy.KnownDimensions] = []

    def measure(
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: str,
        style: waxy.Style,
    ) -> waxy.Size:
        received_kd.append(known_dimensions)
        kw, kh = known_dimensions
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

    mock_measure = MagicMock(
        side_effect=lambda kd, avail, nid, ctx, style: waxy.Size(ctx.width, ctx.height)
    )

    tree.compute_layout(root, measure=mock_measure)

    # The measure function should only have been called for node_with_ctx
    for call in mock_measure.call_args_list:
        # 4th arg (index 3) is context — should never be None
        assert call[0][3] is not None

    # node_without_ctx should get zero intrinsic width (height may stretch from flex)
    layout = tree.layout(node_without_ctx)
    assert layout.size.width == 0.0


def test_measure_error_propagation() -> None:
    tree = waxy.TaffyTree[str]()
    node = tree.new_leaf_with_context(waxy.Style(), "test")
    root = tree.new_with_children(waxy.Style(display=waxy.Display.Flex), [node])

    def bad_measure(
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: str,
        style: waxy.Style,
    ) -> waxy.Size:
        msg = "measure failed!"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="measure failed!"):
        tree.compute_layout(root, measure=bad_measure)


def test_compute_layout_with_available_space_param() -> None:
    tree = waxy.TaffyTree[TextContent]()
    node = tree.new_leaf_with_context(
        waxy.Style(),
        TextContent("Some text"),
    )
    # Give the root an explicit size so it fills the viewport
    root = tree.new_with_children(
        waxy.Style(display=waxy.Display.Flex, size_width=waxy.length(800)),
        [node],
    )

    def measure(
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: TextContent,
        style: waxy.Style,
    ) -> waxy.Size:
        kw, _ = known_dimensions
        w = kw if kw is not None else len(context.text) * 8.0
        return waxy.Size(w, 16.0)

    viewport = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.definite(800.0),
        height=waxy.AvailableSpace.definite(600.0),
    )
    tree.compute_layout(root, measure=measure, available_space=viewport)

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
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: TextContent,
        style: waxy.Style,
    ) -> waxy.Size:
        kw, _ = known_dimensions
        avail_w, _ = available_space

        if kw is not None:
            return waxy.Size(kw, char_height)

        # Max-content: report full single-line width
        if not avail_w.is_definite():
            return waxy.Size(len(context.text) * char_width, char_height)

        # Definite: use the available width
        return waxy.Size(avail_w.value(), char_height)  # type: ignore[arg-type]

    # Default available_space is max-content — node should get full single-line width
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
        known_dimensions: waxy.KnownDimensions,
        available_space: waxy.AvailableDimensions,
        node_id: waxy.NodeId,
        context: TextContent,
        style: waxy.Style,
    ) -> waxy.Size:
        kw, _ = known_dimensions
        avail_w, _ = available_space

        if kw is not None:
            return waxy.Size(kw, char_height)

        if avail_w.is_definite():
            return waxy.Size(avail_w.value(), char_height)  # type: ignore[arg-type]

        text = context.text
        if avail_w.is_min_content():
            # Min-content: width of the longest word
            longest_word = max(text.split(), key=len)
            return waxy.Size(len(longest_word) * char_width, char_height)

        # Max-content: full single-line width
        return waxy.Size(len(text) * char_width, char_height)

    # Use min_content available space
    viewport = waxy.AvailableDimensions(
        width=waxy.AvailableSpace.min_content(),
        height=waxy.AvailableSpace.min_content(),
    )
    tree.compute_layout(root, measure=measure, available_space=viewport)
    layout = tree.layout(text_node)
    # "world" is the longest word (5 chars), so min-content width = 40.0
    assert layout.size.width == len("world") * char_width  # 40.0
    assert layout.size.height == char_height


def test_compute_layout_without_measure_still_works() -> None:
    """Existing behavior: leaf nodes without measure get zero intrinsic size."""
    tree = waxy.TaffyTree()
    style = waxy.Style(
        size_width=waxy.Dimension.length(100.0),
        size_height=waxy.Dimension.length(50.0),
    )
    node = tree.new_leaf(style)
    tree.compute_layout(node)
    layout = tree.layout(node)
    assert layout.size.width == 100.0
    assert layout.size.height == 50.0
