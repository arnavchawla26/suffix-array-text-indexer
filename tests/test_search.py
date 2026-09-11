import random

import pytest

from suffix_array_text_indexer.suffix_array import build_suffix_array
from suffix_array_text_indexer.lcp import build_lcp_array
from suffix_array_text_indexer.search import substring_search, longest_repeated_substring
from tests.oracles import naive_search, naive_longest_repeated_substring


# ---------------------------------------------------------------------------
# substring_search
# ---------------------------------------------------------------------------

class TestSubstringSearchEdgeCases:
    def test_empty_text(self):
        sa = build_suffix_array("")
        assert substring_search("", sa, "") == [0]
        assert substring_search("", sa, "x") == []

    def test_empty_pattern_matches_every_position(self):
        text = "hello"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "") == [0, 1, 2, 3, 4, 5]

    def test_single_char_text(self):
        sa = build_suffix_array("x")
        assert substring_search("x", sa, "x") == [0]
        assert substring_search("x", sa, "y") == []

    def test_pattern_not_found(self):
        text = "the quick brown fox"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "zzz") == []

    def test_pattern_equals_whole_text(self):
        text = "abcdef"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, text) == [0]

    def test_pattern_longer_than_text(self):
        text = "abc"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "abcdef") == []

    def test_repeated_chars(self):
        text = "aaaaaa"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "aa") == [0, 1, 2, 3, 4]
        assert substring_search(text, sa, "aaaaaa") == [0]
        assert substring_search(text, sa, "aaaaaaa") == []

    def test_unicode_text(self):
        text = "héllo wörld héllo"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "héllo") == naive_search(text, "héllo")
        assert substring_search(text, sa, "wörld") == naive_search(text, "wörld")

    def test_overlapping_occurrences(self):
        text = "abababab"
        sa = build_suffix_array(text)
        assert substring_search(text, sa, "aba") == [0, 2, 4]


class TestSubstringSearchAgainstNaive:
    @pytest.mark.parametrize("trial", range(60))
    def test_random_patterns_small_alphabet(self, trial):
        rng = random.Random(trial)
        n = rng.randint(0, 30)
        text = "".join(rng.choice("ab") for _ in range(n))
        sa = build_suffix_array(text)
        for _ in range(5):
            m = rng.randint(0, 5)
            pattern = "".join(rng.choice("ab") for _ in range(m))
            assert substring_search(text, sa, pattern) == naive_search(text, pattern)

    @pytest.mark.parametrize("trial", range(40))
    def test_random_patterns_wider_alphabet(self, trial):
        rng = random.Random(2000 + trial)
        n = rng.randint(0, 60)
        text = "".join(chr(rng.randint(97, 122)) for _ in range(n))
        sa = build_suffix_array(text)
        for _ in range(5):
            m = rng.randint(0, 8)
            pattern = "".join(chr(rng.randint(97, 122)) for _ in range(m))
            assert substring_search(text, sa, pattern) == naive_search(text, pattern)

    def test_patterns_drawn_from_text_always_found(self):
        rng = random.Random(123)
        text = "".join(rng.choice("abcde") for _ in range(300))
        sa = build_suffix_array(text)
        for _ in range(50):
            m = rng.randint(1, 10)
            start = rng.randint(0, len(text) - m)
            pattern = text[start:start + m]
            result = substring_search(text, sa, pattern)
            assert start in result
            assert result == naive_search(text, pattern)


# ---------------------------------------------------------------------------
# longest_repeated_substring
# ---------------------------------------------------------------------------

class TestLongestRepeatedSubstring:
    def test_empty_text(self):
        assert longest_repeated_substring("", [], []) == ("", [])

    def test_single_char(self):
        sa = build_suffix_array("x")
        lcp = build_lcp_array("x", sa)
        assert longest_repeated_substring("x", sa, lcp) == ("", [])

    def test_no_repeats(self):
        text = "abcdefg"
        sa = build_suffix_array(text)
        lcp = build_lcp_array(text, sa)
        assert longest_repeated_substring(text, sa, lcp) == ("", [])

    def test_all_same_char(self):
        text = "aaaa"
        sa = build_suffix_array(text)
        lcp = build_lcp_array(text, sa)
        substring, positions = longest_repeated_substring(text, sa, lcp)
        assert substring == "aaa"
        assert positions == [0, 1]

    def test_banana(self):
        text = "banana"
        sa = build_suffix_array(text)
        lcp = build_lcp_array(text, sa)
        substring, positions = longest_repeated_substring(text, sa, lcp)
        assert substring == "ana"
        assert positions == [1, 3]

    @pytest.mark.parametrize("trial", range(40))
    def test_random_against_naive(self, trial):
        rng = random.Random(trial)
        n = rng.randint(0, 18)
        text = "".join(rng.choice("ab") for _ in range(n))
        sa = build_suffix_array(text)
        lcp = build_lcp_array(text, sa)
        substring, positions = longest_repeated_substring(text, sa, lcp)
        exp_substring, exp_positions = naive_longest_repeated_substring(text)
        assert len(substring) == len(exp_substring)
        # Multiple substrings can tie for longest; verify ours is a
        # genuine repeated substring of the right length rather than
        # requiring an exact string match with the oracle's pick.
        #
        # Note: occurrences can legitimately *overlap* (e.g. "aa" occurs
        # at both position 2 and 3 in "bbaaab"), so counting via
        # str.count() is wrong here -- it only counts non-overlapping
        # matches and would undercount. Use naive_search (which returns
        # every start position, overlaps included) as the ground truth
        # occurrence count instead.
        if substring:
            occurrence_positions = naive_search(text, substring)
            assert len(occurrence_positions) >= 2
            assert positions == occurrence_positions
        else:
            assert exp_substring == ""
