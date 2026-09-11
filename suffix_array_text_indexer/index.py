"""TextIndex: a convenience wrapper bundling a text, its suffix array and
LCP array, plus the query methods built on top of them.
"""

from __future__ import annotations

import json
from typing import List, Tuple

from .suffix_array import build_suffix_array
from .lcp import build_lcp_array
from .search import substring_search, longest_repeated_substring, longest_common_substring


class TextIndex:
    """A prebuilt suffix array + LCP array over a fixed text, with query
    methods. Build once (O(n log^2 n)), then query cheaply and repeatedly.
    """

    def __init__(self, text: str):
        self.text = text
        self.sa: List[int] = build_suffix_array(text)
        self.lcp: List[int] = build_lcp_array(text, self.sa)

    def __len__(self) -> int:
        return len(self.text)

    def search(self, pattern: str) -> List[int]:
        """All occurrence positions of pattern in self.text."""
        return substring_search(self.text, self.sa, pattern)

    def longest_repeated_substring(self) -> Tuple[str, List[int]]:
        """The longest substring of self.text that repeats, and all of
        its occurrence positions."""
        return longest_repeated_substring(self.text, self.sa, self.lcp)

    @staticmethod
    def longest_common_substring(a: str, b: str) -> Tuple[str, List[int], List[int]]:
        """Longest substring common to two strings a and b. Builds its
        own combined generalized suffix array internally; does not use
        any single TextIndex instance's data (this is a two-text query,
        exposed as a static method for a convenient single import path)."""
        return longest_common_substring(a, b)

    def to_json(self) -> str:
        """Serialize this index (text + precomputed sa/lcp) to JSON."""
        return json.dumps({"text": self.text, "sa": self.sa, "lcp": self.lcp})

    @classmethod
    def from_json(cls, data: str) -> "TextIndex":
        """Rebuild a TextIndex from JSON produced by to_json(). Trusts
        the stored sa/lcp rather than recomputing them (fast load)."""
        obj = json.loads(data)
        self = cls.__new__(cls)
        self.text = obj["text"]
        self.sa = obj["sa"]
        self.lcp = obj["lcp"]
        return self
