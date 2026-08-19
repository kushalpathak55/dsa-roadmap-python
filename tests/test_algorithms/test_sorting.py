import random

import pytest

from app.algorithms import sorting

SORT_FUNCTIONS = [
    sorting.bubble_sort,
    sorting.selection_sort,
    sorting.insertion_sort,
    sorting.merge_sort,
    sorting.quick_sort,
    sorting.heap_sort,
]


@pytest.mark.parametrize("sort_fn", SORT_FUNCTIONS)
@pytest.mark.parametrize(
    "arr",
    [
        [5, 3, 8, 1, 9, 2, 7],
        [],
        [1],
        [2, 2, 2],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [random.randint(-50, 50) for _ in range(30)],
    ],
)
def test_sort_produces_correct_final_array(sort_fn, arr):
    steps = list(sort_fn(arr))
    assert steps, "generator must yield at least one step"
    assert steps[-1]["array"] == sorted(arr)
    assert steps[-1]["kind"] == "done"


@pytest.mark.parametrize("sort_fn", SORT_FUNCTIONS)
def test_steps_have_common_envelope(sort_fn):
    steps = list(sort_fn([3, 1, 2]))
    for i, step in enumerate(steps):
        assert step["step_index"] == i
        assert "kind" in step
        assert "note" in step
        assert "counters" in step
        assert "indices" in step
        assert set(step["indices"].keys()) == {"compare", "swap", "pivot", "sorted", "range", "found"}
