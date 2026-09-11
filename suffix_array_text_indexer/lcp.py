"""Kasai's algorithm: build the LCP (Longest Common Prefix) array from a
suffix array in O(n) time.

lcp[i] is the length of the longest common prefix between the suffix at
sa[i] and the suffix at sa[i-1] (its neighbour in sorted order); lcp[0] is
defined to be 0 (there is no predecessor).

Kasai's insight: process suffixes in *text* order (i = 0, 1, 2, ...)
rather than sorted order, and track a running match length h. When we
move from suffix i to suffix i+1, the new match length can only drop by
at most 1 compared to the previous suffix's match length -- so h never
needs to be reset to 0 and decremented from scratch, giving O(n) total
work across all n suffixes instead of O(n) per suffix.
"""

from __future__ import annotations

from typing import List


def build_lcp_array(text: str, sa: List[int]) -> List[int]:
    """Build the LCP array for ``text`` given its suffix array ``sa``."""
    n = len(text)
    if n == 0:
        return []
    if n == 1:
        return [0]

    rank = [0] * n
    for i, suffix_start in enumerate(sa):
        rank[suffix_start] = i

    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    return lcp
