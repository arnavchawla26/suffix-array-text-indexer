import random

import pytest

from suffix_array_text_indexer.search import longest_common_substring
from tests.oracles import naive_lcs


class TestLongestCommonSubstringEdgeCases:
    def test_both_empty(self):
        assert longest_common_substring("", "") == ("", [], [])

    def test_one_empty(self):
        assert longest_common_substring("", "abc") == ("", [], [])
        assert longest_common_substring("abc", "") == ("", [], [])

    def test_identical_strings(self):
        substring, pos_a, pos_b = longest_common_substring("abcdef", "abcdef")
        assert substring == "abcdef"
        assert pos_a == [0]
        assert pos_b == [0]

    def test_no_common_substring(self):
        # Disjoint alphabets guarantee zero overlap.
        substring, pos_a, pos_b = longest_common_substring("abc", "xyz")
        assert substring == ""
        assert pos_a == []
        assert pos_b == []

    def test_single_shared_char(self):
        substring, pos_a, pos_b = longest_common_substring("a", "a")
        assert substring == "a"

    def test_no_overlap_single_chars(self):
        substring, _, _ = longest_common_substring("a", "b")
        assert substring == ""

    def test_classic_example(self):
        # textbook-style example
        a = "xabxac"
        b = "abcabxabcd"
        substring, pos_a, pos_b = longest_common_substring(a, b)
        expected = naive_lcs(a, b)
        assert len(substring) == len(expected)
        assert a[pos_a[0]:pos_a[0] + len(substring)] == substring
        assert b[pos_b[0]:pos_b[0] + len(substring)] == substring

    def test_unicode_strings(self):
        a = "héllo wörld 你好世界"
        b = "wörld héllo 再见世界"
        substring, pos_a, pos_b = longest_common_substring(a, b)
        expected = naive_lcs(a, b)
        assert len(substring) == len(expected)

    def test_substring_at_boundary_of_a(self):
        # Common substring runs right up to the end of `a`.
        a = "prefixCOMMON"
        b = "COMMONsuffix"
        substring, pos_a, pos_b = longest_common_substring(a, b)
        assert substring == "COMMON"

    def test_result_positions_are_verifiably_correct(self):
        a = "banana split banana"
        b = "banana boat"
        substring, pos_a, pos_b = longest_common_substring(a, b)
        assert substring != ""
        for p in pos_a:
            assert a[p:p + len(substring)] == substring
        for p in pos_b:
            assert b[p:p + len(substring)] == substring


class TestLongestCommonSubstringAgainstNaive:
    @pytest.mark.parametrize("trial", range(60))
    def test_random_small_alphabet(self, trial):
        rng = random.Random(trial)
        na = rng.randint(0, 15)
        nb = rng.randint(0, 15)
        a = "".join(rng.choice("ab") for _ in range(na))
        b = "".join(rng.choice("ab") for _ in range(nb))
        substring, pos_a, pos_b = longest_common_substring(a, b)
        expected = naive_lcs(a, b)
        assert len(substring) == len(expected)
        if substring:
            assert substring in a
            assert substring in b
            for p in pos_a:
                assert a[p:p + len(substring)] == substring
            for p in pos_b:
                assert b[p:p + len(substring)] == substring

    @pytest.mark.parametrize("trial", range(40))
    def test_random_wider_alphabet(self, trial):
        rng = random.Random(3000 + trial)
        na = rng.randint(0, 25)
        nb = rng.randint(0, 25)
        a = "".join(rng.choice("abcde") for _ in range(na))
        b = "".join(rng.choice("abcde") for _ in range(nb))
        substring, pos_a, pos_b = longest_common_substring(a, b)
        expected = naive_lcs(a, b)
        assert len(substring) == len(expected)

    def test_sentinel_never_leaks_into_answer(self):
        # If the sentinel-picking logic were broken, the answer could
        # spuriously include the separator character.
        rng = random.Random(55)
        a = "".join(rng.choice("abc") for _ in range(40))
        b = "".join(rng.choice("abc") for _ in range(40))
        substring, _, _ = longest_common_substring(a, b)
        for cp in range(0xE000, 0xE010):
            assert chr(cp) not in substring
