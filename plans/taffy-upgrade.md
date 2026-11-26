# Plan: Upgrade taffy (PR #56)

**Status: In progress.** On taffy 0.16.0; merge waits on [taffy#1354](https://github.com/DioxusLabs/taffy/issues/1354).

This covers moving waxy from taffy 0.14 to 0.16 in [#56](https://github.com/JoshKarpel/waxy/pull/56): the steps an upgrade takes, what the PR has done, what's left, and the questions still open.
It doesn't cover features waxy could add on top of taffy.

## Upgrade Process

The steps for any taffy upgrade, in order:

1. **Read the release notes.**
   The published crate ships no `CHANGELOG.md`, so read the GitHub release
   (`gh release view v<version> -R DioxusLabs/taffy`).
   Sort each item into one of three kinds: it breaks waxy's build, it changes behavior waxy exposes, or it's internal to taffy.
2. **Bump and build.**
   `cargo add taffy@<version>`, then `cargo build`; the compile errors list the breaking API changes waxy hits.
3. **Mirror each new taffy type faithfully** (see "Mirror taffy" in `CLAUDE.md`).
   A type that gains information gets that information exposed, not dropped at the binding.
4. **Recheck the `NoCalc` safety argument** in `src/values.rs`.
   It rests on two facts about taffy: `CompactLength` holds a raw pointer only for `calc()` values, which waxy never constructs, and `taffy::TaffyTree::resolve_calc_value` ignores its argument.
   If `CompactLength` becomes `Send + Sync`, delete `NoCalc` and its `unsafe impl`s instead.
5. **Probe each behavior change** with a short script against the built extension, then correct the `.pyi` docstrings that describe the old behavior.
6. **Run the tests, then the strict xfails as normal tests.**
   A strict xfail that upstream fixed fails the run on its own, but one whose failure mode changed doesn't, so also run them with `--runxfail -n0` and check each still fails for its stated reason.
7. **Update version references:** the `docs.rs/taffy/<version>/` links in `src/values.rs` and `python/waxy/__init__.pyi` (check that each still resolves, since items move between modules), and "Taffy Version" in `CLAUDE.md`.
8. **Re-run `benchmarks/tips.py`** and update any ratio in `docs/performance.md` that moved: taffy releases change hot paths.
9. **Record the user-facing changes in `docs/changelog.md`**, in the section for the waxy release that will ship them.
10. `just check`.

## Done

### taffy 0.14 to 0.15

`docs/changelog.md`'s `0.8.0` section lists the user-facing changes: `Position.Static`, `Fixed`, and `Sticky` with containing-block layout for `Absolute` nodes, `Normal` and `Unsafe*` alignment, `hoisted_children`, rounding in absolute coordinates, `NamedGridLine` resolving like CSS `<custom-ident>`, and more.
The upgrade also brought property tests for `absolute_layouts` (`tests/test_absolute_layouts_properties.py`), which turned up taffy#1354.

### taffy 0.15 to 0.16

- `taffy::Layout::scrollable_overflow_rect` is a `ScrollableOverflow` ([taffy#1372](https://github.com/DioxusLabs/taffy/pull/1372)), which packs a reversed-scroll-origin flag per axis into the signs of `right` and `bottom`.
  `src/layout.rs` reads the rectangle through its accessors, and `Layout.scrollable_overflow_rect` still returns a `Rect` without the flags (see the first open question).
- Reversed flex containers keep their negative overflow, and scroll containers clip what scrolling can't reach.
  A probe of a `column-reverse` container confirmed it: its overflow `top` is negative, and scrolling reaches it from the end edge.
  The stub docstring and changelog say so.
- `calc()` values are a `CalcHandle`, which still wraps a `*const ()`, so `NoCalc` stays; `resolve_calc_value` still ignores the handle.
- The taffy#1354 xfails still fail the same three ways (next section).
- The `docs.rs` links point at 0.16.0, and all of them resolve.

## Blocker: taffy#1354

A node keeps the hoisted-children list from its last layout as a containing block after it stops being one: when it loses its children, or when it or an ancestor becomes hidden.
taffy's rounding pass still walks that stale list.
`tests/test_tree.py` pins three symptoms as strict xfails, each in a `left-a-leaf` and a `hidden` variant where they apply:

- `test_compute_layout_survives_nesting_a_containing_block_in_its_box`: rounding recurses until the stack overflows, killing the process.
- `test_compute_layout_survives_deleting_box_of_emptied_or_hidden_container`: `InvalidNodeId` on every later `compute_layout` after closing a popup.
- `test_rounding_ignores_hoisted_list_of_node_left_a_leaf`: an absolute box is rounded from the stale node's offset.

The issue is open upstream with no fix merged.
[taffy#1378](https://github.com/DioxusLabs/taffy/pull/1378), open, stops hidden subtrees from reading hoisted lists, which by its description covers the `hidden` variants; it says stale lists on visible leaves are "still #1354's problem".

## Remaining Work

- [ ] Re-run `benchmarks/tips.py` on 0.16 (step 8) and update `docs/performance.md` if a ratio moved.
  taffy 0.16 switches node-context lookups to FxHash ([taffy#1402](https://github.com/DioxusLabs/taffy/pull/1402)), which could shift the context-related ratios.
- [ ] Fold the `Unreleased` changelog entries into `0.8.0`, since 0.8.0 hasn't been tagged and will ship 0.16: the upgrade entry becomes "from 0.14 to 0.16", and the overflow entry joins `0.8.0`'s `Changed`.
  Update `0.8.0`'s date when releasing.
- [ ] Settle the open questions below.
- [ ] When upstream fixes taffy#1354: upgrade (the strict xfails fail the run, which shows the fix arrived), drop the `xfail` marks, and update this plan's status.

## Open Questions

### Expose `ScrollableOverflow`'s reversal flags?

Without them, a Python caller can't tell which edge a reversed container's scrolling starts from, so mirroring taffy argues for exposing them.
Options:

- **A `ScrollableOverflow` pyclass** returned by `Layout.scrollable_overflow_rect`, with the edges, a `rect` property, and the flags.
  It mirrors taffy most closely, but it breaks every caller that treats the value as a `Rect`.
  waxy's `Point` holds floats, so taffy's `is_reversed() -> Point<bool>` has to become a `tuple[bool, bool]` or two fields (`is_reversed_x`, `is_reversed_y`).
- **A separate `Layout` property for the flags**, leaving `scrollable_overflow_rect` a `Rect`.
  Nothing breaks, but taffy's one value becomes two properties on `Layout`.
- **Leave them out.**
  No API change, but taffy's reversal information stays out of reach from Python.

### Ship 0.8.0 before taffy#1354 is fixed?

#56 is a draft pending taffy#1354.
Waiting keeps the crash and the `InvalidNodeId` out of a release, but holds back every other change since 0.7.1.
taffy 0.14 has no hoisted lists, so waxy 0.7.1 can't hit these bugs.
Shipping now releases the 0.15 and 0.16 fixes, with the three symptoms above as known issues.
Releasing after taffy#1378 alone would fix only the `hidden` variants.
