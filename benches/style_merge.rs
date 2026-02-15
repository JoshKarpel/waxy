use criterion::{black_box, criterion_group, criterion_main, Criterion};

use _waxy::style::{Style, F_ALL, F_DISPLAY, F_FLEX_GROW, F_FLEX_SHRINK, F_POSITION, F_SIZE_WIDTH};

/// Helper: build a Style with the given set_fields mask.
fn style(mask: u64) -> Style {
    let mut inner = taffy::Style::DEFAULT;
    inner.display = taffy::Display::Grid;
    inner.position = taffy::Position::Absolute;
    inner.flex_grow = 2.0;
    inner.flex_shrink = 0.5;
    Style::from_taffy_with_mask(inner, mask)
}

fn bench_merge(c: &mut Criterion) {
    // Merge where rhs has no fields set (fast path: just clone).
    c.bench_function("merge_no_fields_set", |b| {
        let base = style(F_ALL);
        let overlay = style(0);
        b.iter(|| black_box(base.merge(black_box(&overlay))));
    });

    // Merge where rhs has a few fields set (typical usage).
    c.bench_function("merge_few_fields_set", |b| {
        let base = style(F_ALL);
        let overlay = style(F_DISPLAY | F_FLEX_GROW | F_POSITION);
        b.iter(|| black_box(base.merge(black_box(&overlay))));
    });

    // Merge where rhs has all fields set (worst case).
    c.bench_function("merge_all_fields_set", |b| {
        let base = style(F_ALL);
        let overlay = style(F_ALL);
        b.iter(|| black_box(base.merge(black_box(&overlay))));
    });

    // Three-way chaining: a.merge(&b).merge(&c)
    c.bench_function("merge_chain_3", |b| {
        let a = style(F_DISPLAY | F_POSITION);
        let b_style = style(F_FLEX_GROW | F_FLEX_SHRINK);
        let c_style = style(F_SIZE_WIDTH);
        b.iter(|| black_box(a.merge(black_box(&b_style)).merge(black_box(&c_style))));
    });
}

criterion_group!(benches, bench_merge);
criterion_main!(benches);
