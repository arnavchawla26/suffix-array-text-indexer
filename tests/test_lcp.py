import random

import pytest

from suffix_array_text_indexer.suffix_array import build_suffix_array
from suffix_array_text_indexer.lcp import build_lcp_array
from tests.oracles import naive_lcp_array


class TestBasics:
    def test_empty_string(self):
        assert build_lcp_array("", []) == []

    def test_single_char(self):
        assert build_lcp_array("x", [0]) == [0]

    def test_banana_matches_known_answer(self):
        s = "banana"
        sa = build_suffix_array(s)
        assert sa == [5, 3, 1, 0, 4, 2]
        assert build_lcp_array(s, sa) == [0, 1, 3, 0, 0, 2]

    def test_all_same_char(self):
        s = "aaaaa"
        sa = build_suffix_array(s)
        assert sa == [4, 3, 2, 1, 0]
        lcp = build_lcp_array(s, sa)
        # suffixes sorted: a, aa, aaa, aaaa, aaaaa -> successive common
        # prefixes are 0,1,2,3,4
        assert lcp == [0, 1, 2, 3, 4]


class TestAgainstNaiveOracle:
    @pytest.mark.parametrize("trial", range(60))
    def test_random_small_alphabet(self, trial):
        rng = random.Random(trial)
        n = rng.randint(0, 30)
        s = "".join(rng.choice("ab") for _ in range(n))
        sa = build_suffix_array(s)
        assert build_lcp_array(s, sa) == naive_lcp_array(s, sa)

    @pytest.mark.parametrize("trial", range(40))
    def test_random_medium_alphabet(self, trial):
        rng = random.Random(500 + trial)
        n = rng.randint(0, 35)
        s = "".join(rng.choice("abcdef") for _ in range(n))
        sa = build_suffix_array(s)
        assert build_lcp_array(s, sa) == naive_lcp_array(s, sa)

    def test_unicode_text(self):
        s = "abcabcabc你好你好abc"
        sa = build_suffix_array(s)
        assert build_lcp_array(s, sa) == naive_lcp_array(s, sa)

    def test_larger_random_string(self):
        rng = random.Random(99)
        s = "".join(rng.choice("abcd") for _ in range(1500))
        sa = build_suffix_array(s)
        assert build_lcp_array(s, sa) == naive_lcp_array(s, sa)

    def test_lcp_values_are_bounded_and_consistent(self):
        # lcp[i] can never exceed the length of either neighbouring
        # suffix, and it's genuinely the max common-prefix length.
        rng = random.Random(7)
        s = "".join(rng.choice("abc") for _ in range(200))
        sa = build_suffix_array(s)
        lcp = build_lcp_array(s, sa)
        for i in range(1, len(sa)):
            a, b = s[sa[i - 1]:], s[sa[i]:]
            assert lcp[i] <= min(len(a), len(b))
            assert a[:lcp[i]] == b[:lcp[i]]
            if lcp[i] < min(len(a), len(b)):
                assert a[lcp[i]] != b[lcp[i]]
