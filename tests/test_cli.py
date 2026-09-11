import json
import os

import pytest

from suffix_array_text_indexer.cli import main


@pytest.fixture
def text_file(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("the quick brown fox jumps over the lazy dog\nthe fox runs\n", encoding="utf-8")
    return str(p)


def test_build_writes_index(tmp_path, text_file, capsys):
    out = str(tmp_path / "idx.json")
    rc = main(["build", text_file, "-o", out])
    assert rc == 0
    assert os.path.exists(out)
    with open(out) as f:
        data = json.load(f)
    assert "sa" in data and "lcp" in data and "text" in data
    captured = capsys.readouterr()
    assert "Built index" in captured.out


def test_search_finds_matches(text_file, capsys):
    rc = main(["search", text_file, "fox"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "match(es)" in captured.out
    assert "fox" in captured.out.lower() or "line=" in captured.out


def test_search_no_matches(text_file, capsys):
    rc = main(["search", text_file, "zzzznotfound"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "No matches" in captured.out


def test_search_with_prebuilt_index(tmp_path, text_file, capsys):
    idx_path = str(tmp_path / "idx.json")
    main(["build", text_file, "-o", idx_path])
    capsys.readouterr()
    rc = main(["search", text_file, "quick", "--index", idx_path])
    assert rc == 0
    captured = capsys.readouterr()
    assert "match(es)" in captured.out


def test_lrs(text_file, capsys):
    rc = main(["lrs", text_file])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Longest repeated substring" in captured.out


def test_lcs(tmp_path, capsys):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("the quick brown fox", encoding="utf-8")
    file_b.write_text("a quick brown dog", encoding="utf-8")
    rc = main(["lcs", str(file_a), str(file_b)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Longest common substring" in captured.out
    assert "quick brown" in captured.out


def test_lcs_no_common(tmp_path, capsys):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("aaaa", encoding="utf-8")
    file_b.write_text("zzzz", encoding="utf-8")
    rc = main(["lcs", str(file_a), str(file_b)])
    assert rc == 1
    captured = capsys.readouterr()
    assert "No common substring" in captured.out


def test_benchmark_runs_end_to_end(capsys):
    rc = main([
        "benchmark",
        "--sizes", "200,1000",
        "--pattern-lengths", "3,8",
        "--queries", "5",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Benchmark" in captured.out
    assert "text_n" in captured.out
