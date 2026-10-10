"""Time constructing, merging, and hashing `Style` (plan items 6 and 7)."""

import sys

from workloads import GRID_STYLE_KWARGS, TYPICAL_STYLE_KWARGS, best_of, format_time, report

import waxy


def construction() -> list[tuple[str, str]]:
    """Construction cost by number of fields and by the position of a value in its union."""
    cases: list[tuple[str, dict[str, object]]] = [
        ("Style()", {}),
        ("Style(flex_grow=1)", {"flex_grow": 1}),
        ("Style(size_width=Length(1))", {"size_width": waxy.Length(1)}),
        ("Style(size_width=Percent(1.0))", {"size_width": waxy.Percent(1.0)}),
        ("Style(size_width=AUTO)", {"size_width": waxy.AUTO}),
        ("Style(size_width=STRETCH)", {"size_width": waxy.STRETCH}),
        ("Typical (11 fields)", TYPICAL_STYLE_KWARGS),
        ("Grid with 7 template tracks", GRID_STYLE_KWARGS),
    ]
    return [
        (f"construct {label}", format_time(best_of(lambda k=kwargs: waxy.Style(**k), 200_000)))  # type: ignore[misc]
        for label, kwargs in cases
    ]


def hashing() -> list[tuple[str, str]]:
    """Cost of `hash()` on the same `Style` object, repeatedly."""
    cases = [
        ("Style()", waxy.Style()),
        ("Typical (11 fields)", waxy.Style(**TYPICAL_STYLE_KWARGS)),  # type: ignore[arg-type]
        ("Grid with 7 template tracks", waxy.Style(**GRID_STYLE_KWARGS)),  # type: ignore[arg-type]
    ]
    return [
        (f"hash {label}", format_time(best_of(lambda s=style: hash(s), 1_000_000)))  # type: ignore[misc]
        for label, style in cases
    ]


def merging() -> list[tuple[str, str]]:
    """Cost of `|`, with and without hashing the result."""
    a = waxy.Style(**TYPICAL_STYLE_KWARGS)  # type: ignore[arg-type]
    b = waxy.Style(flex_grow=2.0, margin_top=waxy.Length(1))
    return [
        ("merge (a | b)", format_time(best_of(lambda: a | b, 300_000, repeat=7))),
        ("merge, then first hash", format_time(best_of(lambda: hash(a | b), 300_000, repeat=7))),
        ("sys.getsizeof(Style)", f"{sys.getsizeof(a)} bytes"),
    ]


if __name__ == "__main__":
    report(construction() + hashing() + merging())
