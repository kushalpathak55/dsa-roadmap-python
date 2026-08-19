---
complexity:
  time_best: "O(n * m)"
  time_avg: "O(n * m)"
  time_worst: "O(n * m)"
  space: "O(n * m)"
eli5: >-
  You and a friend each spelled out a secret word using magnet letters on
  the fridge, and you want to find the longest "string of letters" that
  shows up in BOTH words, in the same order - though not necessarily right
  next to each other. You compare letters one at a time, and whenever they
  match, you know you've found part of your shared secret code. Keep
  matching to build the longest one possible!
---
The longest common subsequence of two strings is the longest sequence of
characters that appears in both, *in order* but not necessarily
contiguously - e.g. `"ABCBDAB"` and `"BDCABA"` share the subsequence
`"BCBA"`. It's the algorithm behind `diff`-style tools.

`dp[i][j]` = the LCS length of the first `i` characters of A and the first
`j` characters of B. Each cell has three possible dependencies - one
diagonal, two straight:

```python
def lcs_length(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1       # characters match - extend the diagonal
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # take the better of up/left
    return dp[n][m]
```

**When the characters match**, the answer only ever comes from the
diagonal (`dp[i-1][j-1] + 1`) - matching characters always extend a
subsequence, they're never worth skipping. **When they don't match**, the
best answer so far is whichever is better: dropping the current character
of A (`up`) or of B (`left`). This three-way dependency (diagonal, up,
left) is the step up in complexity from knapsack's two-way one.

The actual subsequence (not just its length) can be recovered by walking
back through the table from `dp[n][m]`: step diagonally on a match, and
step toward whichever neighbor (up or left) supplied the value otherwise.

The demo below fills the table row by row, highlighting the dependency
(diagonal on a match, both straight neighbors otherwise), then reconstructs
the actual subsequence at the end.
