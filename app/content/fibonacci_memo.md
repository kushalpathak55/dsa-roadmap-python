---
complexity:
  time_best: "O(n)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(n)"
eli5: >-
  Imagine adding up a growing pile of numbers, where each new number is
  just the last two added together (1, 1, 2, 3, 5, 8...). Instead of
  re-solving numbers you've already figured out, you write each answer on
  a sticky note. Next time you need that number, you just peek at the
  sticky note instead of doing the math all over again - way faster!
---
The naive recursive Fibonacci (`fib(n) = fib(n-1) + fib(n-2)`) recomputes the
same subproblems over and over - `fib(5)` calls `fib(3)` twice, `fib(2)`
three times, and so on, giving an exponential O(2ⁿ) blowup. Dynamic
programming fixes this by **storing each subproblem's answer the first time
it's computed**, so it's never recomputed.

```python
def fib(n):
    table = [0, 1] + [0] * (n - 1) if n >= 1 else [0]
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table[n]
```

This is the **bottom-up (tabulation)** style: fill in a table from the base
cases upward, in order, so every value it depends on is already computed
by the time it's needed. The alternative - **top-down (memoization)** -
keeps the natural recursive structure but caches each result in a dict the
first time it's computed, returning the cached value on subsequent calls.
Both visit each subproblem exactly once; they differ only in whether the
"which order to fill things in" decision is made explicitly (bottom-up) or
falls out naturally from the recursion (top-down).

**Why this is the simplest possible DP problem:** each cell depends on
exactly two previous cells, and the table is one-dimensional - it sets up
the pattern (fill a table, look up already-solved subproblems) that the
2D problems (knapsack, LCS) build on directly.

The demo below fills the table left to right, highlighting the two cells
each new value depends on.
