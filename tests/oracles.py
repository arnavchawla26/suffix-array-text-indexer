"""Brute-force reference implementations used as test oracles. These are
deliberately naive/independent of the real implementation's algorithms so
they can catch real bugs rather than agreeing by construction.
"""

from __future__ import annotations

from typing import List, Tuple


def naive_suffix_array(s: str) -> List[int]:
    """O(n^2 log n): sort all suffixes as actual Python strings."""
    n = len(s)
    return sorted(range(n), key=lambda i: s[i:])


def naive_lcp_array(s: str, sa: List[int]) -> List[int]:
    """O(n^2): directly compare each adjacent pair of suffixes character
    by character, with no Kasai trick at all."""
    n = len(s)
    lcp = [0] * n
    for i in range(1, n):
        a, b = s[sa[i - 1]:], s[sa[i]:]
        h = 0
        while h < len(a) and h < len(b) and a[h] == b[h]:
            h += 1
        lcp[i] = h
    return lcp


def naive_search(text: str, pattern: str) -> List[int]:
    """O(n*m): every window, direct slice comparison (no str.find)."""
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    return [i for i in range(n - m + 1) if text[i:i + m] == pattern]


def naive_longest_repeated_substring(s: str) -> Tuple[str, List[int]]:
    """O(n^3)-ish: compare every pair of suffixes directly. Only used on
    small strings in tests."""
    n = len(s)
    best_len = 0
    best_start = None
    for i in range(n):
        for j in range(i + 1, n):
            a, b = s[i:], s[j:]
            h = 0
            while h < len(a) and h < len(b) and a[h] == b[h]:
                h += 1
            if h > best_len:
                best_len = h
                best_start = i
    if best_len == 0:
        return "", []
    substring = s[best_start:best_start + best_len]
    positions = naive_search(s, substring)
    return substring, positions


def naive_lcs(a: str, b: str) -> str:
    """Classic O(len(a) * len(b)) dynamic-programming longest common
    substring. Structurally unrelated to the suffix-array approach --
    a genuinely independent cross-check."""
    if not a or not b:
        return ""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best_len = 0
    best_end = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best_len:
                    best_len = dp[i][j]
                    best_end = i
    return a[best_end - best_len:best_end]
