import random

import pytest

from suffix_array_text_indexer.suffix_array import build_suffix_array
from tests.oracles import naive_suffix_array


def _assert_valid_sa(s, sa):
    """A suffix array is valid iff the suffixes it names, read out in
    that order, are non-decreasing lexicographically and it's a genuine
    permutation of 0..n-1."""
    n = len(s)
    assert sorted(sa) == list(range(n))
    for i in range(1, n):
        assert s[sa[i - 1]:] <= s[sa[i]:]


class TestBasics:
    def test_empty_string(self):
        assert build_suffix_array("") == []

    def test_single_char(self):
        assert build_suffix_array("x") == [0]

    def test_two_distinct_chars(self):
        assert build_suffix_array("ba") == [1, 0]

    def test_banana_matches_known_answer(self):
        # Classic textbook example.
        assert build_suffix_array("banana") == [5, 3, 1, 0, 4, 2]


class TestBoundaryOffByOne:
    """The classic doubling-construction gotcha: a suffix that runs off
    the end of the string partway through a comparison must sort as
    smaller than a suffix that has more characters there. Exercise this
    directly rather than only spot-checking, per the project brief."""

    @pytest.mark.parametrize("s", ["aa", "aaa", "aaaa", "aaaaa", "aaaaaa"])
    def test_all_same_char_runs(self, s):
        sa = build_suffix_array(s)
        got_order = [s[i:] for i in sa]
        expected_order = sorted(s[i:] for i in range(len(s)))
        assert got_order == expected_order
        # Shortest suffix ("a") must sort first among an all-same run.
        assert sa[0] == len(s) - 1

    def test_banana_with_explicit_sentinel(self):
        s = "banana$"
        sa = build_suffix_array(s)
        got_order = [s[i:] for i in sa]
        expected_order = sorted(s[i:] for i in range(len(s)))
        assert got_order == expected_order

    @pytest.mark.parametrize(
        "s",
        [
            "abab",
            "ababab",
            "aabaabaa",
            "mississippi",
            "mississippi$",
            "aaaaaaaaaa",
            "xax",
            "abcabcabcabc",
        ],
    )
    def test_prefix_relationships(self, s):
        _assert_valid_sa(s, build_suffix_array(s))


class TestAgainstNaiveOracle:
    @pytest.mark.parametrize("trial", range(60))
    def test_random_small_alphabet(self, trial):
        rng = random.Random(trial)
        n = rng.randint(0, 25)
        alphabet = "ab"
        s = "".join(rng.choice(alphabet) for _ in range(n))
        assert build_suffix_array(s) == naive_suffix_array(s)

    @pytest.mark.parametrize("trial", range(40))
    def test_random_medium_alphabet(self, trial):
        rng = random.Random(1000 + trial)
        n = rng.randint(0, 30)
        alphabet = "abcde"
        s = "".join(rng.choice(alphabet) for _ in range(n))
        assert build_suffix_array(s) == naive_suffix_array(s)

    @pytest.mark.parametrize("trial", range(20))
    def test_random_wide_alphabet(self, trial):
        rng = random.Random(2000 + trial)
        n = rng.randint(0, 40)
        s = "".join(chr(rng.randint(32, 126)) for _ in range(n))
        assert build_suffix_array(s) == naive_suffix_array(s)

    def test_unicode_text(self):
        s = "héllo wörld héllo θεσσαλονίκη 你好世界你好"
        assert build_suffix_array(s) == naive_suffix_array(s)

    @pytest.mark.parametrize("trial", range(10))
    def test_random_unicode(self, trial):
        rng = random.Random(3000 + trial)
        n = rng.randint(0, 25)
        pool = "abc你好θæøü\U0001f600\U0001f642"
        s = "".join(rng.choice(pool) for _ in range(n))
        assert build_suffix_array(s) == naive_suffix_array(s)

    def test_larger_random_string_is_internally_consistent(self):
        # Too big to compare against O(n^2 log n) naive_suffix_array
        # cheaply in a hot loop, but we can still check SA validity.
        rng = random.Random(42)
        s = "".join(rng.choice("abcd") for _ in range(2000))
        sa = build_suffix_array(s)
        _assert_valid_sa(s, sa)
