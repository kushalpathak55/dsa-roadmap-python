"""Two array-scanning techniques that show up constantly in interviews: two
pointers (converge from both ends of a sorted array) and a fixed-size sliding
window (drop one element, add one element, never rescan the whole window).
Both reuse the array-family step schema - no new renderer needed.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.algorithms.common import array_step, predict_prompt


def two_pointer_sum(arr: list[int], target: int) -> Generator[dict[str, Any], None, None]:
    """Find a pair in a SORTED array that sums to target by walking two
    pointers inward from both ends - O(n) after the sort, versus O(n^2) for
    checking every pair."""
    arr = sorted(arr)
    n = len(arr)
    comparisons = 0
    step_index = 0

    def emit(kind: str, note: str, **kwargs) -> dict[str, Any]:
        nonlocal step_index
        step = array_step(step_index=step_index, kind=kind, array=arr, note=note, counters={"comparisons": comparisons}, **kwargs)
        step_index += 1
        return step

    yield emit("start", f"Looking for two numbers that sum to {target} (array sorted first)")

    left, right = 0, n - 1
    while left < right:
        comparisons += 1
        total = arr[left] + arr[right]
        answer = "Equal" if total == target else ("Less than" if total < target else "Greater than")
        yield emit(
            "compare",
            f"{arr[left]} + {arr[right]} = {total} - compare to {target}",
            compare=[left, right],
            range_=[left, right],
            predict=predict_prompt(
                f"Is {arr[left]} + {arr[right]} equal to, less than, or greater than {target}?",
                ["Equal", "Less than", "Greater than"],
                answer,
            ),
        )
        if total == target:
            yield emit(
                "found",
                f"Found it: {arr[left]} + {arr[right]} = {target}",
                found=left,
                compare=[left, right],
                sorted_indices=[left, right],
            )
            return
        if total < target:
            yield emit(
                "move-left",
                f"{total} < {target} - the smallest way to grow the sum is to move the left pointer right",
                compare=[left, right],
            )
            left += 1
        else:
            yield emit(
                "move-right",
                f"{total} > {target} - the only way to shrink the sum is to move the right pointer left",
                compare=[left, right],
            )
            right -= 1

    yield emit("not_found", f"No pair sums to {target}")


def sliding_window_max_sum(arr: list[int], k: int) -> Generator[dict[str, Any], None, None]:
    """Find the maximum-sum contiguous window of size k by sliding one
    element at a time - each slide drops the outgoing element and adds the
    incoming one, so the whole window is never re-summed from scratch."""
    arr = list(arr)
    n = len(arr)
    step_index = 0
    window_sum = sum(arr[:k])
    best_sum = window_sum
    best_start = 0

    def emit(kind: str, note: str, **kwargs) -> dict[str, Any]:
        nonlocal step_index
        step = array_step(
            step_index=step_index,
            kind=kind,
            array=arr,
            note=note,
            counters={"window_sum": window_sum, "best_sum": best_sum},
            **kwargs,
        )
        step_index += 1
        return step

    yield emit("start", f"Sliding a window of size {k} across the array")
    yield emit("window", f"First window [0..{k - 1}] sums to {window_sum}", range_=[0, k - 1])

    for end in range(k, n):
        start = end - k + 1
        dropped = arr[start - 1]
        added = arr[end]
        new_sum = window_sum - dropped + added
        is_new_best = new_sum > best_sum
        yield emit(
            "slide",
            f"Slide: drop {dropped}, add {added} -> {window_sum} - {dropped} + {added} = {new_sum}",
            range_=[start, end],
            compare=[start - 1, end],
            predict=predict_prompt(
                f"Will the new window sum ({new_sum}) beat the current best ({best_sum})?",
                ["Yes", "No"],
                "Yes" if is_new_best else "No",
            ),
        )
        window_sum = new_sum
        if is_new_best:
            best_sum = window_sum
            best_start = start
            yield emit("new-best", f"New best window sum: {best_sum} (starting at index {start})", range_=[start, end])

    yield emit(
        "done",
        f"Best window sum: {best_sum}, starting at index {best_start}",
        range_=[best_start, best_start + k - 1],
        sorted_indices=list(range(best_start, best_start + k)),
    )
