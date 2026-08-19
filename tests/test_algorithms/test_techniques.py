import itertools
import random

import pytest

from app.algorithms import techniques


@pytest.mark.parametrize("seed", range(50))
def test_two_pointer_sum_matches_brute_force(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 15)
    arr = [rng.randint(-15, 15) for _ in range(n)]
    target = rng.choice(arr) + rng.choice(arr)

    steps = list(techniques.two_pointer_sum(arr, target))
    last = steps[-1]
    found = last["kind"] == "found"
    brute_force_found = any(a + b == target for a, b in itertools.combinations(sorted(arr), 2))

    assert found == brute_force_found
    if found:
        i, j = last["indices"]["compare"]
        assert last["array"][i] + last["array"][j] == target


def test_two_pointer_sum_envelope():
    steps = list(techniques.two_pointer_sum([5, 3, 8, 1, 9, 2, 7], 12))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] in ("found", "not_found")
    assert steps[0]["array"] == sorted([5, 3, 8, 1, 9, 2, 7])


@pytest.mark.parametrize("seed", range(50))
def test_sliding_window_max_sum_matches_brute_force(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 15)
    arr = [rng.randint(-15, 15) for _ in range(n)]
    k = rng.randint(1, n)

    steps = list(techniques.sliding_window_max_sum(arr, k))
    last = steps[-1]
    expected_best = max(sum(arr[i : i + k]) for i in range(n - k + 1))

    assert last["counters"]["best_sum"] == expected_best


def test_sliding_window_max_sum_envelope():
    steps = list(techniques.sliding_window_max_sum([5, 3, 8, 1, 9, 2, 7], 3))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[-1]["counters"]["best_sum"] == 18  # window [8, 1, 9]
