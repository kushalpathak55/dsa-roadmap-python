"""Sorting algorithms as step generators. Each yields full-array-snapshot steps
(see app/algorithms/common.py) so the front-end player never re-derives state -
it only renders what's given.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.algorithms.common import array_step, predict_prompt


def _make_emitter(arr: list[int], state: dict[str, Any]):
    def emit(kind: str, note: str, **kwargs) -> dict[str, Any]:
        sorted_indices = kwargs.pop("sorted_indices", sorted(state["sorted_set"]))
        counters = {k: v for k, v in state.items() if k not in ("step_index", "sorted_set")}
        step = array_step(
            step_index=state["step_index"],
            kind=kind,
            array=arr,
            note=note,
            sorted_indices=sorted_indices,
            counters=counters,
            **kwargs,
        )
        state["step_index"] += 1
        return step

    return emit


def bubble_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "swaps": 0, "sorted_set": set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            state["comparisons"] += 1
            will_swap = arr[j] > arr[j + 1]
            yield emit(
                "compare",
                f"Comparing {arr[j]} and {arr[j + 1]}",
                compare=[j, j + 1],
                predict=predict_prompt(f"Will {arr[j]} and {arr[j + 1]} be swapped?", ["Yes", "No"], "Yes" if will_swap else "No"),
            )
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                state["swaps"] += 1
                swapped = True
                yield emit("swap", f"Swapped {arr[j + 1]} and {arr[j]}", swap=[j, j + 1])
        state["sorted_set"].add(n - i - 1)
        if not swapped:
            state["sorted_set"].update(range(n))
            break

    state["sorted_set"].update(range(n))
    yield emit("done", "Array sorted")


def selection_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "swaps": 0, "sorted_set": set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    for i in range(n):
        min_idx = i
        yield emit("select", f"Assume index {i} ({arr[i]}) is the minimum", pivot=[min_idx])
        for j in range(i + 1, n):
            state["comparisons"] += 1
            will_be_new_min = arr[j] < arr[min_idx]
            yield emit(
                "compare",
                f"Comparing {arr[j]} with current min {arr[min_idx]}",
                compare=[min_idx, j],
                pivot=[min_idx],
                predict=predict_prompt(f"Will {arr[j]} become the new minimum?", ["Yes", "No"], "Yes" if will_be_new_min else "No"),
            )
            if arr[j] < arr[min_idx]:
                min_idx = j
                yield emit("new-min", f"New minimum {arr[min_idx]} at index {min_idx}", pivot=[min_idx])
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            state["swaps"] += 1
            yield emit("swap", f"Swapped {arr[i]} into position {i}", swap=[i, min_idx])
        state["sorted_set"].add(i)

    yield emit("done", "Array sorted")


def insertion_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "shifts": 0, "sorted_set": {0} if n else set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        yield emit("select", f"Inserting {key} into the sorted prefix", pivot=[i])
        while j >= 0:
            state["comparisons"] += 1
            will_shift = arr[j] > key
            yield emit(
                "compare",
                f"Comparing {key} with {arr[j]}",
                compare=[j],
                predict=predict_prompt(f"Will {key} shift past {arr[j]}?", ["Yes", "No"], "Yes" if will_shift else "No"),
            )
            if not will_shift:
                break
            state["shifts"] += 1
            arr[j + 1] = arr[j]
            yield emit("shift", f"Shifted {arr[j + 1]} right", swap=[j, j + 1])
            j -= 1
        arr[j + 1] = key
        state["sorted_set"] = set(range(i + 1))
        yield emit("place", f"Placed {key} at index {j + 1}", pivot=[j + 1])

    yield emit("done", "Array sorted")


def merge_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "writes": 0, "sorted_set": set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    def merge(lo: int, mid: int, hi: int):
        left = arr[lo : mid + 1]
        right = arr[mid + 1 : hi + 1]
        yield emit("range", f"Merging [{lo}, {mid}] with [{mid + 1}, {hi}]", range_=[lo, hi])
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            state["comparisons"] += 1
            smaller = left[i] if left[i] <= right[j] else right[j]
            # Skip the prompt on a tie - both options would show the same label.
            tie_predict = None if left[i] == right[j] else predict_prompt(
                f"Which is smaller: {left[i]} or {right[j]}?", [left[i], right[j]], smaller
            )
            # No index highlight here (unlike every other sort): left[i]/right[j]
            # are snapshots taken before this merge started, but arr is being
            # overwritten in place as we go, so as soon as any element from the
            # other side has been written (j > 0), position lo+i in the live
            # array no longer holds left[i] - highlighting it would point at
            # the wrong bar. The range_ highlight plus the note (which always
            # names the true values) carry this step instead.
            yield emit(
                "compare",
                f"Comparing {left[i]} and {right[j]}",
                range_=[lo, hi],
                predict=tie_predict,
            )
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            state["writes"] += 1
            yield emit("write", f"Placed {arr[k]} at index {k}", swap=[k], range_=[lo, hi])
            k += 1
        while i < len(left):
            arr[k] = left[i]
            state["writes"] += 1
            yield emit("write", f"Placed remaining {arr[k]} at index {k}", swap=[k], range_=[lo, hi])
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            state["writes"] += 1
            yield emit("write", f"Placed remaining {arr[k]} at index {k}", swap=[k], range_=[lo, hi])
            j += 1
            k += 1
        state["sorted_set"].update(range(lo, hi + 1))
        yield emit("merged", f"Range [{lo}, {hi}] merged", range_=[lo, hi])

    def merge_sort_rec(lo: int, hi: int):
        if lo >= hi:
            if lo == hi:
                state["sorted_set"].add(lo)
            return
        mid = (lo + hi) // 2
        yield from merge_sort_rec(lo, mid)
        yield from merge_sort_rec(mid + 1, hi)
        yield from merge(lo, mid, hi)

    yield from merge_sort_rec(0, n - 1)
    state["sorted_set"].update(range(n))
    yield emit("done", "Array sorted")


def quick_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "swaps": 0, "sorted_set": set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    def partition(lo: int, hi: int):
        pivot = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            state["comparisons"] += 1
            goes_left = arr[j] < pivot
            yield emit(
                "compare",
                f"Comparing {arr[j]} with pivot {pivot}",
                compare=[j, hi],
                pivot=[hi],
                range_=[lo, hi],
                predict=predict_prompt(f"Will {arr[j]} go to the left of pivot {pivot}?", ["Yes", "No"], "Yes" if goes_left else "No"),
            )
            if arr[j] < pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    state["swaps"] += 1
                    yield emit("swap", f"Swapped {arr[j]} and {arr[i]}", swap=[i, j], pivot=[hi], range_=[lo, hi])
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        state["swaps"] += 1
        yield emit("swap", f"Moved pivot {arr[i + 1]} into place", swap=[i + 1, hi], pivot=[i + 1], range_=[lo, hi])
        return i + 1

    def quick_sort_rec(lo: int, hi: int):
        if lo > hi:
            return
        if lo == hi:
            state["sorted_set"].add(lo)
            return
        yield emit("range", f"Partitioning range [{lo}, {hi}], pivot {arr[hi]}", range_=[lo, hi], pivot=[hi])
        p = yield from partition(lo, hi)
        state["sorted_set"].add(p)
        yield emit("sorted", f"Pivot {arr[p]} now in its final position", sorted_indices=sorted(state["sorted_set"]), pivot=[p])
        yield from quick_sort_rec(lo, p - 1)
        yield from quick_sort_rec(p + 1, hi)

    yield from quick_sort_rec(0, n - 1)
    state["sorted_set"].update(range(n))
    yield emit("done", "Array sorted")


def heap_sort(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    n = len(arr)
    state = {"step_index": 0, "comparisons": 0, "swaps": 0, "sorted_set": set()}
    emit = _make_emitter(arr, state)

    yield emit("start", "Initial array")

    def sift_down(heap_size: int, root: int):
        while True:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < heap_size:
                state["comparisons"] += 1
                left_bigger = arr[left] > arr[largest]
                yield emit(
                    "compare",
                    f"Is {arr[left]} bigger than the current largest, {arr[largest]}?",
                    compare=[left, largest],
                    predict=predict_prompt(f"Is {arr[left]} bigger than {arr[largest]}?", ["Yes", "No"], "Yes" if left_bigger else "No"),
                )
                if left_bigger:
                    largest = left

            if right < heap_size:
                state["comparisons"] += 1
                right_bigger = arr[right] > arr[largest]
                yield emit(
                    "compare",
                    f"Is {arr[right]} bigger than the current largest, {arr[largest]}?",
                    compare=[right, largest],
                    predict=predict_prompt(f"Is {arr[right]} bigger than {arr[largest]}?", ["Yes", "No"], "Yes" if right_bigger else "No"),
                )
                if right_bigger:
                    largest = right

            if largest == root:
                break
            arr[root], arr[largest] = arr[largest], arr[root]
            state["swaps"] += 1
            yield emit("swap", f"Swapped {arr[largest]} and {arr[root]} to sift down", swap=[root, largest])
            root = largest

    # Build a max-heap out of the whole array: sift down every non-leaf node,
    # starting from the last one and working back to the root.
    for i in range(n // 2 - 1, -1, -1):
        yield from sift_down(n, i)
    if n:
        yield emit("heap-built", "Max-heap built - the largest value is now at the root")

    # Repeatedly swap the root (the max of what's left) to the end of the
    # shrinking heap, then sift down to restore the heap property.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        state["swaps"] += 1
        state["sorted_set"].add(end)
        yield emit("swap", f"Moved max {arr[end]} to its final position", swap=[0, end])
        yield from sift_down(end, 0)

    state["sorted_set"].update(range(n))
    yield emit("done", "Array sorted")
