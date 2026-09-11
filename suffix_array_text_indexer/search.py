"""Applications built on top of a suffix array + LCP array:

1. substring_search    -- all occurrence positions of a pattern, O(m log n)
2. longest_repeated_substring -- read directly off the max of the LCP array
3. longest_common_substring   -- generalized suffix array over A + $ + B
"""

from __future__ import annotations

from typing import List, Tuple

from .suffix_array import build_suffix_array
from .lcp import build_lcp_array


# ---------------------------------------------------------------------------
# 1. Substring search
# ---------------------------------------------------------------------------

def _compare_prefix(text: str, suffix_start: int, pattern: str) -> int:
    """Compare the first len(pattern) characters of the suffix starting at
    suffix_start against pattern. Returns -1, 0, or 1.

    Relies on ordinary Python string comparison: if the suffix has fewer
    than len(pattern) characters remaining, the slice comes out shorter
    than pattern, and Python already orders a strict prefix as "less than"
    the longer string it's a prefix of -- which is exactly the semantics
    we want (a suffix that runs out before the pattern does can't match,
    and sorts before it).
    """
    m = len(pattern)
    chunk = text[suffix_start:suffix_start + m]
    if chunk < pattern:
        return -1
    if chunk > pattern:
        return 1
    return 0


def substring_search(text: str, sa: List[int], pattern: str) -> List[int]:
    """Return every starting position in ``text`` where ``pattern``
    occurs, using two binary searches over the suffix array to find the
    contiguous range of suffixes that start with ``pattern``.

    O(m log n) where m = len(pattern), n = len(text).
    """
    n = len(text)
    if len(pattern) == 0:
        # Convention matching brute force `[i for i in range(n+1) if
        # text[i:i+0] == ""]`: the empty pattern "occurs" at every
        # position, including the end-of-text position.
        return list(range(n + 1))
    if len(pattern) > n:
        return []

    # Lower bound: first index in sa whose suffix is >= pattern.
    lo, hi = 0, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if _compare_prefix(text, sa[mid], pattern) < 0:
            lo = mid + 1
        else:
            hi = mid
    left = lo

    # Upper bound: first index in sa whose suffix is > pattern.
    lo, hi = left, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if _compare_prefix(text, sa[mid], pattern) <= 0:
            lo = mid + 1
        else:
            hi = mid
    right = lo

    return sorted(sa[left:right])


# ---------------------------------------------------------------------------
# 2. Longest repeated substring
# ---------------------------------------------------------------------------

def longest_repeated_substring(
    text: str, sa: List[int], lcp: List[int]
) -> Tuple[str, List[int]]:
    """Find the longest substring of ``text`` that occurs at two or more
    distinct positions. The answer is read directly off the maximum entry
    of the LCP array: that maximum is, by construction, the longest common
    prefix shared by two *adjacent* (in sorted order) suffixes, which is
    exactly the longest repeated substring.

    Returns (substring, sorted list of all its occurrence positions).
    Returns ("", []) if there is no repeated substring (e.g. all
    characters distinct, or text too short to repeat anything).
    """
    if not lcp or max(lcp) == 0:
        return "", []

    max_len = max(lcp)
    idx = lcp.index(max_len)
    start = sa[idx]
    substring = text[start:start + max_len]
    positions = substring_search(text, sa, substring)
    return substring, positions


# ---------------------------------------------------------------------------
# 3. Longest common substring between two strings
# ---------------------------------------------------------------------------

def _pick_sentinel(a: str, b: str) -> str:
    """Pick a single character guaranteed not to appear in ``a`` or
    ``b``, to use as a separator when concatenating the two strings for a
    generalized suffix array. Tries Unicode noncharacters and the private
    use area first (these are reserved and essentially never appear in
    real text), then falls back to an exhaustive scan of the full Unicode
    range if truly necessary.
    """
    used = set(a) | set(b)

    # Unicode noncharacters (U+FDD0..U+FDEF, and U+xFFFE/U+xFFFF of every
    # plane) plus the Private Use Area are reserved for exactly this sort
    # of internal-use purpose and are never valid in interchanged text.
    candidates = list(range(0xFDD0, 0xFDF0))
    candidates += [0xFFFE, 0xFFFF]
    candidates += list(range(0xE000, 0xF8FF + 1))
    for cp in candidates:
        c = chr(cp)
        if c not in used:
            return c

    for cp in range(0x10FFFF, -1, -1):
        c = chr(cp)
        if c not in used:
            return c

    raise ValueError(
        "cannot find a sentinel character: input strings together use "
        "every Unicode code point"
    )


def longest_common_substring(a: str, b: str) -> Tuple[str, List[int], List[int]]:
    """Find the longest substring common to both ``a`` and ``b``.

    Builds one suffix array + LCP array over a + sentinel + b, then scans
    *adjacent* LCP entries: the maximum LCP between two adjacent suffixes
    that originate from different original strings is exactly the longest
    common substring's length. (Adjacent pairs suffice, not just an
    heuristic: if the true optimal pair (p in A, q in B) is not adjacent
    in sorted order, every suffix lexicographically between them shares at
    least their common prefix length, and since that span must contain a
    switch from an A-origin suffix to a B-origin one somewhere, some
    *adjacent* pair inside the span has LCP >= LCP(p, q) -- which, since
    (p, q) was already the maximum possible, means it equals LCP(p, q).)

    Returns (substring, sorted positions in a, sorted positions in b).
    Returns ("", [], []) if there is no common substring, or if either
    input is empty.

    Note: multiple *different* substrings can tie for the longest common
    length (e.g. a="abbbbbbaabaa", b="babaabbabbbab" both contain the
    unrelated length-4 substrings "abbb" and "bbba"). Only positions of
    the one substring actually returned are reported -- scanning adjacent
    LCP entries only tells us the winning *length*; a second, independent
    substring_search pass over the combined text (for the winning
    substring specifically) is needed to avoid conflating occurrence
    positions of unrelated tied-length substrings under one answer.
    """
    if not a or not b:
        return "", [], []

    sentinel = _pick_sentinel(a, b)
    combined = a + sentinel + b
    sep = len(a)  # index of the sentinel character in combined

    sa = build_suffix_array(combined)
    lcp = build_lcp_array(combined, sa)

    def origin(pos: int):
        if pos < sep:
            return "A"
        if pos == sep:
            return None
        return "B"

    best_len = 0
    exemplar_start = None
    for i in range(1, len(sa)):
        o1, o2 = origin(sa[i - 1]), origin(sa[i])
        if o1 is None or o2 is None or o1 == o2:
            continue
        length = lcp[i]
        if length > best_len:
            best_len = length
            exemplar_start = sa[i - 1]

    if best_len == 0:
        return "", [], []

    substring = combined[exemplar_start:exemplar_start + best_len]

    # Now find every occurrence of *this specific* substring (not other
    # substrings that happened to tie for the same length), and sort
    # positions by which original string they came from.
    all_positions = substring_search(combined, sa, substring)
    positions_a = sorted(p for p in all_positions if origin(p) == "A")
    positions_b = sorted(p - sep - 1 for p in all_positions if origin(p) == "B")

    return substring, positions_a, positions_b
