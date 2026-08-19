"""N-Queens by backtracking: try each column in a row, place a queen if it's
not attacked, recurse into the next row, and undo ("backtrack") whenever a
branch runs out of options - including after finding a full solution, since
this demo finds ALL of them rather than stopping at the first. Reuses the
DP-family grid step schema and renderer - a chessboard is just a grid.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.algorithms.common import dp_step, predict_prompt

QUEEN = "♛"


def n_queens_demo(n: int) -> Generator[dict[str, Any], None, None]:
    board: list[int | None] = [None] * n
    step_index = 0
    solutions_found = 0

    def grid_snapshot() -> list[list[Any]]:
        return [[QUEEN if board[r] == c else None for c in range(n)] for r in range(n)]

    def placed_cells() -> list[tuple[int, int]]:
        return [(r, board[r]) for r in range(n) if board[r] is not None]

    def emit(
        kind: str,
        note: str,
        cursor: dict[str, int] | None = None,
        predict: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal step_index
        step = dp_step(
            step_index=step_index,
            kind=kind,
            grid=grid_snapshot(),
            note=note,
            cursor=cursor,
            highlight_cells=placed_cells(),
            row_labels=[str(r) for r in range(n)],
            col_labels=[str(c) for c in range(n)],
            counters={"placed": sum(1 for x in board if x is not None), "solutions": solutions_found},
            predict=predict,
        )
        step_index += 1
        return step

    def is_safe(row: int, col: int) -> bool:
        for r in range(row):
            c = board[r]
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def solve(row: int) -> Generator[dict[str, Any], None, None]:
        nonlocal solutions_found
        if row == n:
            solutions_found += 1
            yield emit("solution", f"Solution {solutions_found}: every row has a safe queen")
            return

        for col in range(n):
            safe = is_safe(row, col)
            yield emit(
                "try",
                f"Row {row}: is column {col} safe (no queen attacks it)?",
                cursor={"row": row, "col": col},
                predict=predict_prompt(f"Is ({row}, {col}) safe for a queen?", ["Yes", "No"], "Yes" if safe else "No"),
            )
            if not safe:
                continue
            board[row] = col
            yield emit("place", f"Placing a queen at ({row}, {col})", cursor={"row": row, "col": col})
            yield from solve(row + 1)
            board[row] = None
            yield emit("backtrack", f"Backtrack: no more options below ({row}, {col}) - removing this queen", cursor={"row": row, "col": col})

    yield emit("start", f"Solving {n}-Queens - place {n} queens so none attack each other")
    yield from solve(0)
    yield emit("done", f"Done - found {solutions_found} solution{'s' if solutions_found != 1 else ''}")
