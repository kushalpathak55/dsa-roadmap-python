import random

import pytest

from app.algorithms.trie import trie_demo


def _brute_outcome(words: list[str], query: str) -> str:
    if query in words:
        return "found"
    prefixes = {w[:i] for w in words for i in range(1, len(w) + 1)}
    if query in prefixes:
        return "prefix-only"
    return "not-found"


@pytest.mark.parametrize("seed", range(50))
def test_trie_search_outcomes_match_brute_force(seed):
    rng = random.Random(seed)
    alphabet = "abc"
    n = rng.randint(1, 6)
    words = ["".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(n)]

    steps = list(trie_demo(words))
    phase_indices = [i for i, s in enumerate(steps) if s["kind"] == "phase"]

    for idx in phase_indices:
        query = steps[idx]["note"].split('"')[1]
        terminal = next(s for s in steps[idx + 1 :] if s["kind"] in ("found", "prefix-only", "not-found"))
        assert terminal["kind"] == _brute_outcome(words, query)


def test_trie_shares_prefixes_in_node_count():
    steps = list(trie_demo(["cat", "car", "card", "care", "dog", "do"]))
    last_insert = [s for s in steps if s["kind"] in ("word-complete", "already-word")][-1]
    unique_prefixes = {w[:i] for w in ["cat", "car", "card", "care", "dog", "do"] for i in range(1, len(w) + 1)}
    assert last_insert["counters"]["nodes"] == len(unique_prefixes) + 1  # +1 for the root


def test_trie_envelope():
    steps = list(trie_demo(["cat"]))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[0]["nodes"] == [{"id": "n0", "value": "•", "parent": None, "state": "default"}]


def test_trie_reinserting_same_word_is_handled():
    steps = list(trie_demo(["cat", "cat"]))
    kinds = [s["kind"] for s in steps]
    assert "word-complete" in kinds
    assert "already-word" in kinds


def test_trie_word_that_is_also_a_prefix_of_another():
    # "do" is a complete word AND a prefix of "dog" - is_word must survive
    # regardless of which order the two are inserted in.
    steps = list(trie_demo(["do", "dog"]))
    complete_notes = [s["note"] for s in steps if s["kind"] in ("word-complete", "already-word")]
    assert any('"do"' in n for n in complete_notes)
    assert any('"dog"' in n for n in complete_notes)
