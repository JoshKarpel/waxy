# Benchmarks

Scripts for measuring waxy's per-call costs, for anyone changing a hot path.
They time the Python-facing API end to end, binding overhead included,
since that's what callers pay.
They don't benchmark taffy's layout algorithms on their own.

- `suite.py` times every operation a frame-by-frame caller performs,
  and saves or compares results.
- `ab.py` compares two builds of the extension module by alternating them.
- `tips.py` measures the ratios that [`docs/performance.md`](../docs/performance.md) states.
- `measure_calls.py` counts calls into the measure callback.
- `workloads.py` holds the trees, styles and timing helpers the others share.

## Run against a release build

A debug build's timings say nothing about what users see.
`just bench` builds with the release profile (fat LTO, so it takes a minute) and runs the suite;
`just bench-build` only builds.
`just build` and `just test` go back to a debug build afterwards.

## Compare builds, not runs

A result saved with `--save` and compared later with `--compare` also measures
whatever else the machine was doing in between.
On a shared or loaded machine, unchanged cases drift by 10% or more between runs.
To judge a change, build each side, keep both copies of the extension module,
and let `ab.py` alternate them:

```text
just bench-build && cp python/waxy/_waxy.*.so /tmp/before.so   # at the baseline
just bench-build && cp python/waxy/_waxy.*.so /tmp/after.so    # with the change
cd benchmarks && uv run python ab.py /tmp/before.so /tmp/after.so -k compute
```

Read the cases the change can't affect as the control:
if they moved, so did the machine.

## Bound a cost before fixing it

The cheapest way to learn what a piece of the hot path costs is to remove it and measure what's
left: return a constant instead of calling Python, skip the memo, and so on,
switched by an environment variable in a throwaway build.
For a cost inside taffy itself, time the same tree in a pure-Rust `examples/` program
(`cargo run --release --example <name>`, with `taffy` already a dependency).
If waxy's time matches it, the binding isn't the problem.

## Profile

`perf` needs `kernel.perf_event_paranoid` at 1 or lower to profile user space.
Build with debug info and frame pointers, record a script that loops the workload,
and read the result with [samply](https://github.com/mstange/samply):

```text
CARGO_PROFILE_RELEASE_DEBUG=true RUSTFLAGS="-Cforce-frame-pointers=yes --cfg pyo3_disable_reference_pool" \
  uv run maturin develop --release
perf record --call-graph fp --freq 2000 -o /tmp/waxy.data -- "$(uv run python -c 'import sys; print(sys.executable)')" workload.py
samply import /tmp/waxy.data
```

`RUSTFLAGS` replaces the `rustflags` in `.cargo/config.toml`, so the profiling build repeats them.
Resolve symbols against the extension module (`python/waxy/_waxy.*.so`), not the interpreter.
