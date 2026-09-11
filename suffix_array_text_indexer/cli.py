"""sitext: a small CLI over the suffix array text indexer.

Subcommands:
    build     Build an index (suffix array + LCP array) from a text file
              and save it to JSON.
    search    Grep-like substring search, printing matching line/col and
              occurrence positions. Builds the index on the fly unless
              --index is given.
    lrs       Longest repeated substring in a text file.
    lcs       Longest common substring between two text files.
    benchmark Time suffix-array substring search vs. naive Python
              scanning (str.find / regex) across a range of text/pattern
              sizes, and print a comparison table.
"""

from __future__ import annotations

import argparse
import random
import re
import sys
import time
from typing import List, Optional, Sequence

from .index import TextIndex
from .search import substring_search
from .suffix_array import build_suffix_array


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _line_col(text: str, pos: int) -> tuple:
    """1-based (line, col) for a character offset pos in text."""
    line = text.count("\n", 0, pos) + 1
    line_start = text.rfind("\n", 0, pos) + 1
    col = pos - line_start + 1
    return line, col


def _line_text(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end]


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def cmd_build(args: argparse.Namespace) -> int:
    text = _read_text(args.text_file)
    t0 = time.perf_counter()
    idx = TextIndex(text)
    elapsed = time.perf_counter() - t0
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(idx.to_json())
    print(
        f"Built index over {len(text)} characters in {elapsed:.4f}s "
        f"-> wrote {args.output}"
    )
    return 0


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def cmd_search(args: argparse.Namespace) -> int:
    if args.index:
        with open(args.index, "r", encoding="utf-8") as f:
            idx = TextIndex.from_json(f.read())
    else:
        text = _read_text(args.text_file)
        idx = TextIndex(text)

    positions = idx.search(args.pattern)
    if not positions:
        print(f"No matches for {args.pattern!r}")
        return 1

    print(f"{len(positions)} match(es) for {args.pattern!r}:")
    for pos in positions:
        line, col = _line_col(idx.text, pos)
        line_text = _line_text(idx.text, pos)
        print(f"  pos={pos} line={line} col={col}: {line_text}")
    return 0


# ---------------------------------------------------------------------------
# lrs
# ---------------------------------------------------------------------------

def cmd_lrs(args: argparse.Namespace) -> int:
    text = _read_text(args.text_file)
    idx = TextIndex(text)
    substring, positions = idx.longest_repeated_substring()
    if not substring:
        print("No repeated substring found.")
        return 1
    print(f"Longest repeated substring ({len(substring)} chars): {substring!r}")
    print(f"Occurs at {len(positions)} position(s): {positions}")
    return 0


# ---------------------------------------------------------------------------
# lcs
# ---------------------------------------------------------------------------

def cmd_lcs(args: argparse.Namespace) -> int:
    a = _read_text(args.file_a)
    b = _read_text(args.file_b)
    substring, positions_a, positions_b = TextIndex.longest_common_substring(a, b)
    if not substring:
        print("No common substring found.")
        return 1
    print(f"Longest common substring ({len(substring)} chars): {substring!r}")
    print(f"  positions in {args.file_a}: {positions_a}")
    print(f"  positions in {args.file_b}: {positions_b}")
    return 0


# ---------------------------------------------------------------------------
# benchmark
# ---------------------------------------------------------------------------

def _random_text(n: int, alphabet: str, seed: int) -> str:
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(n))


def _naive_find_all(text: str, pattern: str) -> List[int]:
    """Naive substring search using repeated str.find (this is what a
    grep-like tool without an index would do)."""
    if not pattern:
        return list(range(len(text) + 1))
    positions = []
    start = 0
    while True:
        i = text.find(pattern, start)
        if i == -1:
            break
        positions.append(i)
        start = i + 1
    return positions


def _naive_regex_all(text: str, pattern: str) -> List[int]:
    """Naive substring search using re.finditer with an escaped literal
    pattern (the other common "no index" approach)."""
    if not pattern:
        return list(range(len(text) + 1))
    return [m.start() for m in re.finditer(re.escape(pattern), text)]


def cmd_benchmark(args: argparse.Namespace) -> int:
    sizes = [int(x) for x in args.sizes.split(",")]
    pattern_lengths = [int(x) for x in args.pattern_lengths.split(",")]
    queries_per_case = args.queries
    alphabet = "ACGT" if args.alphabet == "dna" else "abcdefghij"

    print(
        f"Benchmark: alphabet={args.alphabet!r} ({len(alphabet)} symbols), "
        f"{queries_per_case} queries per case\n"
    )
    header = (
        f"{'text_n':>8} {'pat_m':>6} {'build_s':>10} "
        f"{'sa_query_s':>12} {'find_query_s':>13} {'regex_query_s':>14} "
        f"{'sa_vs_find':>11}"
    )
    print(header)
    print("-" * len(header))

    for n in sizes:
        text = _random_text(n, alphabet, seed=n)
        t0 = time.perf_counter()
        sa = build_suffix_array(text)
        build_time = time.perf_counter() - t0

        for m in pattern_lengths:
            if m > n:
                continue
            rng = random.Random(1000 * n + m)
            patterns = []
            for _ in range(queries_per_case):
                start = rng.randrange(0, n - m + 1)
                patterns.append(text[start:start + m])

            t0 = time.perf_counter()
            for p in patterns:
                substring_search(text, sa, p)
            sa_query_time = time.perf_counter() - t0

            t0 = time.perf_counter()
            for p in patterns:
                _naive_find_all(text, p)
            find_query_time = time.perf_counter() - t0

            t0 = time.perf_counter()
            for p in patterns:
                _naive_regex_all(text, p)
            regex_query_time = time.perf_counter() - t0

            speedup = find_query_time / sa_query_time if sa_query_time > 0 else float("inf")
            print(
                f"{n:>8} {m:>6} {build_time:>10.4f} "
                f"{sa_query_time:>12.5f} {find_query_time:>13.5f} "
                f"{regex_query_time:>14.5f} {speedup:>10.2f}x"
            )
    print(
        "\nNote: build_s is paid once per text size and amortizes across "
        "all queries; sa_query_s/find_query_s/regex_query_s are each the "
        "total time for all queries_per_case queries at that (text_n, "
        "pat_m). sa_vs_find is find_query_s / sa_query_s (>1 means the "
        "suffix array search was faster in aggregate)."
    )
    return 0


# ---------------------------------------------------------------------------
# argument parser / entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sitext",
        description="Suffix array + LCP array text indexing toolkit.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build an index from a text file.")
    p_build.add_argument("text_file")
    p_build.add_argument("-o", "--output", default="index.json")
    p_build.set_defaults(func=cmd_build)

    p_search = sub.add_parser("search", help="Substring search (grep-like).")
    p_search.add_argument("text_file", help="Text file to search (ignored if --index given).")
    p_search.add_argument("pattern")
    p_search.add_argument("--index", help="Prebuilt index JSON from `build`.")
    p_search.set_defaults(func=cmd_search)

    p_lrs = sub.add_parser("lrs", help="Longest repeated substring.")
    p_lrs.add_argument("text_file")
    p_lrs.set_defaults(func=cmd_lrs)

    p_lcs = sub.add_parser("lcs", help="Longest common substring between two files.")
    p_lcs.add_argument("file_a")
    p_lcs.add_argument("file_b")
    p_lcs.set_defaults(func=cmd_lcs)

    p_bench = sub.add_parser(
        "benchmark", help="Time suffix-array search vs. naive scanning."
    )
    p_bench.add_argument("--sizes", default="1000,10000,100000")
    p_bench.add_argument("--pattern-lengths", default="4,16,64", dest="pattern_lengths")
    p_bench.add_argument("--queries", type=int, default=200)
    p_bench.add_argument("--alphabet", choices=["dna", "text"], default="text")
    p_bench.set_defaults(func=cmd_benchmark)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
