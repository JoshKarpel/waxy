"""
Compare two builds of the extension module by running the suite against each in turn.

Results saved by one `suite.py --save` and compared by a later `--compare` drift with whatever
else the machine is doing between the two runs. Alternating the builds round by round, and
keeping each case's best time across rounds, exposes both to the same conditions.

```text
just bench-build && cp python/waxy/_waxy.*.so /tmp/before.so   # at the baseline
just bench-build && cp python/waxy/_waxy.*.so /tmp/after.so    # with the change
uv run python benchmarks/ab.py /tmp/before.so /tmp/after.so -k compute --rounds 3
```

The installed module is restored when the comparison finishes.
"""

import argparse
import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

from workloads import format_time

BENCHMARKS = Path(__file__).parent
INSTALLED = BENCHMARKS.parent / "python" / "waxy" / f"_waxy{sysconfig.get_config_var('EXT_SUFFIX')}"


def install(build: Path) -> None:
    """Put `build` where the editable install loads the extension module from."""
    # Replace through a rename rather than writing in place: a process that still has the old file
    # mapped keeps a valid copy, where overwriting its pages would crash it.
    staged = INSTALLED.with_suffix(".staged")
    shutil.copyfile(build, staged)
    staged.replace(INSTALLED)


def run_suite(output: Path, case_filter: str) -> dict[str, float]:
    """Run the suite in a fresh interpreter, so it loads whichever build is installed now."""
    subprocess.run(
        [sys.executable, "suite.py", "--repeat", "3", "-k", case_filter, "--save", str(output)],
        cwd=BENCHMARKS,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    results: dict[str, float] = json.loads(output.read_text())
    return results


def main() -> None:
    """Alternate the two builds, then print each case's best time under each and their ratio."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("before", type=Path, help="the baseline build of the extension module")
    parser.add_argument("after", type=Path, help="the build to compare against it")
    parser.add_argument(
        "-k", "--filter", default="", help="only run cases whose name contains this"
    )
    parser.add_argument("--rounds", type=int, default=3, help="suite runs per build")
    args = parser.parse_args()

    best: dict[str, dict[str, float]] = {"before": {}, "after": {}}
    with tempfile.TemporaryDirectory() as scratch:
        original = Path(scratch) / "original.so"
        shutil.copyfile(INSTALLED, original)
        try:
            for round_index in range(args.rounds):
                for side in ("before", "after"):
                    install(getattr(args, side))
                    output = Path(scratch) / f"{side}-{round_index}.json"
                    for name, seconds in run_suite(output, args.filter).items():
                        best[side][name] = min(seconds, best[side].get(name, seconds))
        finally:
            install(original)

    width = max(len(name) for name in best["before"])
    for name, before in best["before"].items():
        after = best["after"][name]
        print(
            f"{name:<{width}}  {format_time(before):>10}  {format_time(after):>10}"
            f"  {after / before:.2f}x"
        )


if __name__ == "__main__":
    main()
