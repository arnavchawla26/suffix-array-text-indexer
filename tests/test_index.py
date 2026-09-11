from suffix_array_text_indexer import TextIndex


def test_basic_roundtrip():
    idx = TextIndex("banana")
    assert idx.sa == [5, 3, 1, 0, 4, 2]
    assert idx.search("ana") == [1, 3]
    substring, positions = idx.longest_repeated_substring()
    assert substring == "ana"
    assert positions == [1, 3]


def test_json_roundtrip():
    idx = TextIndex("mississippi")
    data = idx.to_json()
    idx2 = TextIndex.from_json(data)
    assert idx2.text == idx.text
    assert idx2.sa == idx.sa
    assert idx2.lcp == idx.lcp
    assert idx2.search("ssi") == idx.search("ssi")


def test_static_lcs_method():
    substring, pos_a, pos_b = TextIndex.longest_common_substring("hello world", "world hello")
    assert substring != ""


def test_len():
    idx = TextIndex("hello")
    assert len(idx) == 5


def test_empty_text_index():
    idx = TextIndex("")
    assert idx.sa == []
    assert idx.lcp == []
    assert idx.search("x") == []
    assert idx.search("") == [0]
