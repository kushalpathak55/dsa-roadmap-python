import pytest

from app.algorithms import dp


def _expected_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@pytest.mark.parametrize("n", [0, 1, 2, 5, 10, 20])
def test_fibonacci_memo_matches_expected_value(n):
    steps = list(dp.fibonacci_memo_demo(n))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[-1]["grid"][0][n] == _expected_fib(n)


def test_fibonacci_grid_is_always_2d_even_though_conceptually_1d():
    steps = list(dp.fibonacci_memo_demo(5))
    for step in steps:
        assert len(step["grid"]) == 1
        assert len(step["grid"][0]) == 6


def test_fibonacci_highlights_the_two_prior_cells_it_depends_on():
    steps = list(dp.fibonacci_memo_demo(5))
    fill_steps = [s for s in steps if s["kind"] == "fill"]
    for step in fill_steps:
        cols = sorted(c for _, c in step["highlight"]["cells"])
        assert cols == [step["cursor"]["col"] - 2, step["cursor"]["col"] - 1]


def _brute_force_knapsack(capacity, weights, values):
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        total_w = sum(weights[i] for i in range(n) if mask & (1 << i))
        total_v = sum(values[i] for i in range(n) if mask & (1 << i))
        if total_w <= capacity:
            best = max(best, total_v)
    return best


@pytest.mark.parametrize(
    "capacity,weights,values",
    [
        (10, [2, 3, 4, 5], [3, 4, 5, 6]),
        (0, [1, 2], [10, 20]),
        (5, [10], [100]),
        (7, [1, 3, 4, 5], [1, 4, 5, 7]),
    ],
)
def test_knapsack_matches_brute_force(capacity, weights, values):
    steps = list(dp.knapsack_demo(capacity, weights, values))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[-1]["grid"][-1][-1] == _brute_force_knapsack(capacity, weights, values)


def test_knapsack_grid_shape_matches_items_and_capacity():
    steps = list(dp.knapsack_demo(5, [1, 2, 3], [10, 20, 30]))
    final = steps[-1]["grid"]
    assert len(final) == 4  # 3 items + base row
    assert all(len(row) == 6 for row in final)  # capacity 0..5


def _is_subsequence(sub, s):
    it = iter(s)
    return all(ch in it for ch in sub)


@pytest.mark.parametrize(
    "a,b",
    [
        ("ABCBDAB", "BDCABA"),
        ("AGGTAB", "GXTXAYB"),
        ("ABC", "ABC"),
        ("ABC", "XYZ"),
        ("A", "A"),
    ],
)
def test_lcs_length_and_reconstructed_subsequence_are_valid(a, b):
    steps = list(dp.lcs_demo(a, b))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    length = steps[-1]["grid"][-1][-1]

    # extract the reconstructed subsequence from the closing note: `LCS length: N ("XYZ")`
    note = steps[-1]["note"]
    subsequence = note.split('"')[1]
    assert len(subsequence) == length
    assert _is_subsequence(subsequence, a)
    assert _is_subsequence(subsequence, b)


def test_lcs_of_identical_strings_is_the_whole_string():
    steps = list(dp.lcs_demo("ABCDE", "ABCDE"))
    assert steps[-1]["grid"][-1][-1] == 5


def test_lcs_of_disjoint_strings_is_zero():
    steps = list(dp.lcs_demo("ABC", "XYZ"))
    assert steps[-1]["grid"][-1][-1] == 0


def test_every_dp_step_has_the_common_envelope_and_grid_schema():
    steps = list(dp.lcs_demo("AB", "BA"))
    for i, step in enumerate(steps):
        assert step["step_index"] == i
        assert "kind" in step and "note" in step and "counters" in step
        assert "grid" in step and "row_labels" in step and "col_labels" in step
        assert "highlight" in step and "cells" in step["highlight"]
