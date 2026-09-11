"""Suffix array construction via prefix doubling.

The classic "doubling" algorithm: maintain a rank array where rank[i] is
the rank of the suffix starting at i among all suffixes, considering only
their first k characters. Each round doubles k by sorting suffixes on the
key (rank[i], rank[i + k]) -- i.e. the concatenation of two already-sorted
k-length blocks -- and re-deriving ranks from the new order. After
O(log n) rounds every suffix has a unique rank and the ranks *are* the
suffix array's inverse permutation.

Complexity note (worth being precise about): each round performs one
Python `list.sort(key=...)` over n elements, which is O(n log n), and
there are O(log n) rounds, so this implementation is O(n log^2 n) overall
-- not O(n log n). The "O(n log n) doubling construction" name is the
textbook label for the *algorithmic structure* (as opposed to O(n^2 log n)
naive sorting of all suffixes, or O(n) DC3/SA-IS constructions); reaching
true O(n log n) requires replacing the comparison sort in each round with
a linear-time radix sort on the (rank[i], rank[i+k]) pairs. The task scope
here explicitly allows using Python's stable comparison sort instead, so
that final radix-sort step is intentionally skipped.

The classic off-by-one gotcha: when i + k runs past the end of the string,
that suffix has "no second half" and must sort as strictly smaller than
any suffix that *does* have a second half at that offset (a suffix that is
a prefix of another suffix must sort before it). We handle this by using
-1 as the rank for any out-of-range offset, since -1 is guaranteed smaller
than every real rank (ranks are always >= 0).
"""

from __future__ import annotations

from typing import List


def build_suffix_array(text: str) -> List[int]:
    """Build the suffix array of ``text`` via prefix doubling.

    Returns a list of length len(text) containing a permutation of
    0..len(text)-1, giving the starting indices of all suffixes of
    ``text`` sorted in ascending lexicographic order.
    """
    n = len(text)
    if n == 0:
        return []
    if n == 1:
        return [0]

    sa = list(range(n))
    rank = [ord(c) for c in text]
    k = 1

    while True:
        # key(i) = (rank[i], rank[i+k]) with -1 standing in for "past the
        # end of the string" so shorter suffixes sort first.
        def second(i: int, _rank=rank, _k=k, _n=n) -> int:
            j = i + _k
            return _rank[j] if j < _n else -1

        sa.sort(key=lambda i: (rank[i], second(i)))

        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for idx in range(1, n):
            prev, curr = sa[idx - 1], sa[idx]
            same = rank[prev] == rank[curr] and second(prev) == second(curr)
            new_rank[curr] = new_rank[prev] + (0 if same else 1)
        rank = new_rank

        if rank[sa[-1]] == n - 1:
            # All ranks distinct: suffixes are fully, uniquely ordered.
            break
        k *= 2
        if k > n:
            # Safety net: once k exceeds n, (rank[i], rank[i+k]) can no
            # longer distinguish any further pair that isn't already
            # distinguished, so further rounds would be no-ops. This only
            # triggers if the "all ranks distinct" check above didn't
            # already break (it always should for a well-formed run, but
            # keeping this guard makes the loop provably terminating).
            break

    return sa
