"""Unit tests for the pretraining_like corpus resolver (L1 D2; CPU, no downloads)."""
import pytest

from prabodha.lens.adapter import _prompts


def _write_corpus(tmp_path, n_lines=10, words_per_line=24):
    f = tmp_path / "corpus.txt"
    f.write_text(
        "\n".join(" ".join(f"w{i}_{j}" for j in range(words_per_line)) for i in range(n_lines))
        + "\n",
        encoding="utf-8",
    )
    return f


def test_pretraining_like_reads_corpus_file(tmp_path):
    f = _write_corpus(tmp_path, n_lines=10)
    ps = _prompts({"corpus": "pretraining_like", "corpus_file": str(f), "n_prompts": 8})
    assert len(ps) == 8
    assert all(p.strip() and len(p.split()) == 24 for p in ps)


def test_pretraining_like_is_deterministic(tmp_path):
    f = _write_corpus(tmp_path)
    cfg = {"corpus": "pretraining_like", "corpus_file": str(f), "n_prompts": 4}
    assert _prompts(cfg) == _prompts(cfg)


def test_pretraining_like_missing_file_raises(tmp_path):
    cfg = {"corpus": "pretraining_like", "corpus_file": str(tmp_path / "nope.txt"), "n_prompts": 4}
    with pytest.raises(FileNotFoundError):
        _prompts(cfg)


def test_pretraining_like_too_few_prompts_raises(tmp_path):
    f = _write_corpus(tmp_path, n_lines=3)
    cfg = {"corpus": "pretraining_like", "corpus_file": str(f), "n_prompts": 8}
    with pytest.raises(ValueError, match="n_prompts"):
        _prompts(cfg)


def test_unknown_corpus_still_raises():
    with pytest.raises(NotImplementedError):
        _prompts({"corpus": "no_such_corpus", "n_prompts": 4})
