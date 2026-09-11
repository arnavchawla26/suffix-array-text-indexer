"""suffix_array_text_indexer: a from-scratch suffix array + LCP array text
indexing library.

Public API:
    build_suffix_array(text) -> list[int]
    build_lcp_array(text, sa) -> list[int]
    substring_search(text, sa, pattern) -> list[int]
    longest_repeated_substring(text, sa, lcp) -> (str, list[int])
    longest_common_substring(a, b) -> (str, list[int], list[int])
    TextIndex -- convenience class bundling all of the above.
"""

from .suffix_array import build_suffix_array
from .lcp import build_lcp_array
from .search import (
    substring_search,
    longest_repeated_substring,
    longest_common_substring,
)
from .index import TextIndex

__all__ = [
    "build_suffix_array",
    "build_lcp_array",
    "substring_search",
    "longest_repeated_substring",
    "longest_common_substring",
    "TextIndex",
]

__version__ = "1.0.0"
