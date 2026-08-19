---
complexity:
  time_best: "O(n!)"
  time_avg: "O(n!)"
  time_worst: "O(n!)"
  space: "O(n)"
eli5: >-
  Imagine placing chess queens on a board one row at a time, and every
  queen can attack in a straight line or diagonally. You place a queen in
  row 1 wherever looks fine, then row 2, then row 3 - but if you ever reach
  a row where EVERY spot is attacked by a queen already on the board, you
  don't give up: you erase your most recent queen and try the next spot for
  her instead. If that whole row runs out of spots too, you erase THAT
  queen as well and back up another row. It's like working through a maze
  by trying a path, and the moment you hit a dead end, walking back to the
  last fork and trying the other direction instead of starting the maze
  over from scratch.
---
Backtracking explores a search space by building a solution incrementally
and abandoning ("backtracking" out of) any partial solution the moment it's
provably no longer possible to complete correctly - rather than either
checking every full combination (way too slow) or committing to guesses it
can never undo (greedy, which doesn't work here).

```python
def solve_n_queens(n):
    board = [None] * n  # board[row] = column of that row's queen
    solutions = []

    def is_safe(row, col):
        for r in range(row):
            c = board[r]
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def place(row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                place(row + 1)
                board[row] = None  # backtrack

    place(0)
    return solutions
```

The key move is `board[row] = None` right after the recursive call returns -
whether that call found solutions or not, this row's queen has done its job
and gets removed so the loop can try the *next* column. That single undo is
the entire "backtracking" part; everything else is a normal recursive
search. `is_safe` is what prunes the search: the moment a column is attacked,
every solution built on top of it is skipped entirely, without ever being
constructed.

This demo finds **every** solution, not just the first - so watch for it
backtracking even right after a full board is completed, still hunting for
more. That's deliberate: it's the clearest proof the search is genuinely
exhaustive, not just lucky.

**When to use it:** any "build a valid configuration piece by piece, with
constraints that can rule out a partial attempt early" problem - Sudoku,
subsets/permutations, maze/path finding, constraint satisfaction generally.
