"""Searching algorithms as step generators, sharing the array-family step schema with sorting."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.algorithms.common import array_step, predict_prompt


def linear_search(arr: list[int], target: int) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    comparisons = 0
    step_index = 0

    def emit(kind: str, note: str, **kwargs) -> dict[str, Any]:
        nonlocal step_index
        step = array_step(
            step_index=step_index,
            kind=kind,
            array=arr,
            note=note,
            counters={"comparisons": comparisons},
            **kwargs,
        )
        step_index += 1
        return step

    yield emit("start", f"Searching for {target}")

    for i, value in enumerate(arr):
        comparisons += 1
        yield emit(
            "compare",
            f"Checking index {i}: is {value} == {target}?",
            compare=[i],
            predict=predict_prompt(f"Is {value} equal to {target}?", ["Yes", "No"], "Yes" if value == target else "No"),
        )
        if value == target:
            yield emit("found", f"Found {target} at index {i}", found=i, sorted_indices=[i])
            return

    yield emit("not_found", f"{target} not found in the array")


def binary_search(arr: list[int], target: int) -> Generator[dict[str, Any], None, None]:
    arr = sorted(arr)
    n = len(arr)
    comparisons = 0
    step_index = 0

    def emit(kind: str, note: str, **kwargs) -> dict[str, Any]:
        nonlocal step_index
        step = array_step(
            step_index=step_index,
            kind=kind,
            array=arr,
            note=note,
            counters={"comparisons": comparisons},
            **kwargs,
        )
        step_index += 1
        return step

    yield emit("start", f"Searching for {target} (array sorted first: binary search requires sorted input)")

    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        yield emit(
            "narrow",
            f"Checking middle index {mid}: is {arr[mid]} == {target}?",
            compare=[mid],
            range_=[lo, hi],
            predict=predict_prompt(f"Is {arr[mid]} equal to {target}?", ["Yes", "No"], "Yes" if arr[mid] == target else "No"),
        )
        if arr[mid] == target:
            yield emit("found", f"Found {target} at index {mid}", found=mid, range_=[lo, hi], sorted_indices=[mid])
            return
        if arr[mid] < target:
            yield emit("narrow", f"{arr[mid]} < {target}, searching right half", compare=[mid], range_=[mid + 1, hi])
            lo = mid + 1
        else:
            yield emit("narrow", f"{arr[mid]} > {target}, searching left half", compare=[mid], range_=[lo, mid - 1])
            hi = mid - 1

    yield emit("not_found", f"{target} not found in the array", range_=[lo, hi])
