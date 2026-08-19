"""Dynamic programming demos: fibonacci (1D table), 0/1 knapsack (2D), and
longest common subsequence (2D with a diagonal dependency). Each fills its
table bottom-up and yields a step per cell, using the dp-family schema
(app/algorithms/common.py:dp_step) - a grid is always 2D, even fibonacci's
single row, so one dp_grid.js renderer covers all three.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.algorithms.common import dp_step, predict_prompt


def fibonacci_memo_demo(n: int) -> Generator[dict[str, Any], None, None]:
    grid: list[list[int | None]] = [[None] * (n + 1)]
    col_labels = [str(i) for i in range(n + 1)]
    step_index = 0

    def emit(kind: str, note: str, cursor_col: int | None = None, highlight_cols: list[int] | None = None, predict=None):
        nonlocal step_index
        cursor = {"row": 0, "col": cursor_col} if cursor_col is not None else None
        highlight = [(0, c) for c in (highlight_cols or [])]
        step = dp_step(
            step_index=step_index,
            kind=kind,
            grid=grid,
            note=note,
            cursor=cursor,
            highlight_cells=highlight,
            row_labels=["fib"],
            col_labels=col_labels,
            counters={"computed": sum(1 for v in grid[0] if v is not None)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty table")

    grid[0][0] = 0
    yield emit("base", "Base case: fib(0) = 0", cursor_col=0)

    if n >= 1:
        grid[0][1] = 1
        yield emit("base", "Base case: fib(1) = 1", cursor_col=1)

    for i in range(2, n + 1):
        a, b = grid[0][i - 1], grid[0][i - 2]
        correct = a + b
        distractors = [d for d in (correct + 1, max(correct - 1, 0)) if d != correct]
        options = [correct, *distractors][:3]
        grid[0][i] = correct
        yield emit(
            "fill",
            f"fib({i}) = fib({i - 1}) + fib({i - 2}) = {a} + {b} = {grid[0][i]}",
            cursor_col=i,
            highlight_cols=[i - 1, i - 2],
            predict=predict_prompt(f"What is fib({i}) = {a} + {b}?", options, correct),
        )

    yield emit("done", f"fib({n}) = {grid[0][n]}", cursor_col=n)


def knapsack_demo(capacity: int, weights: list[int], values: list[int]) -> Generator[dict[str, Any], None, None]:
    n = len(weights)
    grid: list[list[int | None]] = [[None] * (capacity + 1) for _ in range(n + 1)]
    row_labels = ["∅"] + [f"item {i + 1} (w={weights[i]}, v={values[i]})" for i in range(n)]
    col_labels = [str(w) for w in range(capacity + 1)]
    step_index = 0

    def emit(kind: str, note: str, cursor=None, highlight_cells=None, counters=None, predict=None):
        nonlocal step_index
        step = dp_step(
            step_index=step_index,
            kind=kind,
            grid=grid,
            note=note,
            cursor=cursor,
            highlight_cells=highlight_cells,
            row_labels=row_labels,
            col_labels=col_labels,
            counters=counters if counters is not None else {"filled": sum(1 for row in grid for v in row if v is not None)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty table")

    for w in range(capacity + 1):
        grid[0][w] = 0
    yield emit("base", "Base case: 0 items available -> value 0 for every capacity")

    for i in range(1, n + 1):
        weight, value = weights[i - 1], values[i - 1]
        for w in range(capacity + 1):
            if weight > w:
                grid[i][w] = grid[i - 1][w]
                yield emit(
                    "fill",
                    f"item {i} (w={weight}) doesn't fit in capacity {w} - carry down dp[{i - 1}][{w}] = {grid[i][w]}",
                    cursor={"row": i, "col": w},
                    highlight_cells=[(i - 1, w)],
                )
            else:
                exclude = grid[i - 1][w]
                include = value + grid[i - 1][w - weight]
                grid[i][w] = max(exclude, include)
                yield emit(
                    "fill",
                    f"item {i} at capacity {w}: max(skip={exclude}, take={value}+dp[{i - 1}][{w - weight}]={include}) = {grid[i][w]}",
                    cursor={"row": i, "col": w},
                    highlight_cells=[(i - 1, w), (i - 1, w - weight)],
                    predict=predict_prompt(
                        f"At capacity {w}, is it better to take item {i} (w={weight}, v={value}) or skip it?",
                        ["Take it", "Skip it"],
                        "Take it" if include >= exclude else "Skip it",
                    ),
                )

    yield emit(
        "done",
        f"Best value with capacity {capacity}: {grid[n][capacity]}",
        cursor={"row": n, "col": capacity},
        counters={"filled": (n + 1) * (capacity + 1), "best_value": grid[n][capacity]},
    )


def lcs_demo(a: str, b: str) -> Generator[dict[str, Any], None, None]:
    n, m = len(a), len(b)
    grid: list[list[int | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    row_labels = ["∅", *list(a)]
    col_labels = ["∅", *list(b)]
    step_index = 0

    def emit(kind: str, note: str, cursor=None, highlight_cells=None, counters=None, predict=None):
        nonlocal step_index
        step = dp_step(
            step_index=step_index,
            kind=kind,
            grid=grid,
            note=note,
            cursor=cursor,
            highlight_cells=highlight_cells,
            row_labels=row_labels,
            col_labels=col_labels,
            counters=counters if counters is not None else {"filled": sum(1 for row in grid for v in row if v is not None)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty table")

    for i in range(n + 1):
        grid[i][0] = 0
    for j in range(m + 1):
        grid[0][j] = 0
    yield emit("base", "Base case: an empty string shares no characters with anything - first row/column are 0")

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = a[i - 1] == b[j - 1]
            predict = predict_prompt(
                f"Do '{a[i - 1]}' and '{b[j - 1]}' match?",
                ["Match", "No match"],
                "Match" if match else "No match",
            )
            if match:
                grid[i][j] = grid[i - 1][j - 1] + 1
                yield emit(
                    "fill",
                    f"'{a[i - 1]}' == '{b[j - 1]}': dp[{i}][{j}] = dp[{i - 1}][{j - 1}] + 1 = {grid[i][j]}",
                    cursor={"row": i, "col": j},
                    highlight_cells=[(i - 1, j - 1)],
                    predict=predict,
                )
            else:
                up, left = grid[i - 1][j], grid[i][j - 1]
                grid[i][j] = max(up, left)
                yield emit(
                    "fill",
                    f"'{a[i - 1]}' != '{b[j - 1]}': dp[{i}][{j}] = max(up={up}, left={left}) = {grid[i][j]}",
                    cursor={"row": i, "col": j},
                    highlight_cells=[(i - 1, j), (i, j - 1)],
                    predict=predict,
                )

    # Backtrack to reconstruct the actual subsequence for the closing note.
    subsequence: list[str] = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            subsequence.append(a[i - 1])
            i -= 1
            j -= 1
        elif grid[i - 1][j] >= grid[i][j - 1]:
            i -= 1
        else:
            j -= 1
    subsequence.reverse()

    yield emit(
        "done",
        f"LCS length: {grid[n][m]} (\"{''.join(subsequence)}\")",
        cursor={"row": n, "col": m},
        counters={"filled": (n + 1) * (m + 1), "length": grid[n][m]},
    )
