---
complexity:
  time_best: "O(n * W)"
  time_avg: "O(n * W)"
  time_worst: "O(n * W)"
  space: "O(n * W)"
eli5: >-
  You're packing a backpack for a trip, but it can only hold so much
  weight, and every toy you could bring makes you a different amount of
  happy! You want the HAPPIEST backpack possible without going over the
  weight limit. Instead of trying every single combination (which would
  take forever), you cleverly build up the answer: "what's the best I can
  do with just these first few toys and this much space?" - solving small
  versions first and reusing those answers for bigger ones.
---
Given `n` items, each with a weight and a value, and a knapsack that holds
at most `W` total weight, which items maximize total value? The "0/1" means
each item is taken whole or not at all - no splitting.

The table is `dp[i][w]` = the best value achievable using only the first
`i` items with capacity `w`. Each cell has exactly two candidates: **skip**
item `i` (carry down `dp[i-1][w]`), or **take** it, if it fits (`dp[i-1][w -
weight_i] + value_i`) - the cell is whichever of those is larger.

```python
def knapsack(capacity, weights, values):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] > w:
                dp[i][w] = dp[i - 1][w]                       # doesn't fit - skip
            else:
                dp[i][w] = max(
                    dp[i - 1][w],                               # skip
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],  # take
                )
    return dp[n][capacity]
```

Brute force tries every subset of items - O(2ⁿ). Dynamic programming
instead notices there are only `n * W` distinct subproblems (a prefix of
items × a capacity), and each one is solved in O(1) once its two
dependencies are known - so the whole table fills in O(n·W).

The demo below fills the table row by row (one row per item), highlighting
the "skip" and "take" cells each new value is computed from.
