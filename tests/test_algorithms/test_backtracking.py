from app.algorithms.backtracking import n_queens_demo

KNOWN_SOLUTION_COUNTS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10}


def _is_valid_placement(grid: list[list], n: int) -> bool:
    positions = []
    for row in grid:
        queens_in_row = [c for c, cell in enumerate(row) if cell == "♛"]
        if len(queens_in_row) != 1:
            return False
        positions.append(queens_in_row[0])
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            c1, c2 = positions[r1], positions[r2]
            if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                return False
    return True


def test_n_queens_solution_counts_match_known_values():
    for n, expected in KNOWN_SOLUTION_COUNTS.items():
        steps = list(n_queens_demo(n))
        assert steps[-1]["counters"]["solutions"] == expected


def test_n_queens_every_solution_step_is_a_valid_placement():
    steps = list(n_queens_demo(4))
    solution_steps = [s for s in steps if s["kind"] == "solution"]
    assert len(solution_steps) == 2
    for step in solution_steps:
        assert _is_valid_placement(step["grid"], 4)


def test_n_queens_envelope():
    steps = list(n_queens_demo(4))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[0]["grid"] == [[None] * 4 for _ in range(4)]


def test_n_queens_backtracks_after_a_solution_is_found():
    # This demo finds ALL solutions, so for n=4 (2 solutions) it must keep
    # searching (and therefore backtrack) even after the first is found.
    steps = list(n_queens_demo(4))
    first_solution_idx = next(i for i, s in enumerate(steps) if s["kind"] == "solution")
    assert any(s["kind"] == "backtrack" for s in steps[first_solution_idx:])


def test_n_queens_zero_solutions_for_two_and_three():
    for n in (2, 3):
        steps = list(n_queens_demo(n))
        assert not any(s["kind"] == "solution" for s in steps)
        assert steps[-1]["counters"]["solutions"] == 0
