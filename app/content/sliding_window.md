---
complexity:
  time_best: "O(n)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(1)"
eli5: >-
  Imagine a flashlight that only lights up 3 boxes in a row at a time, and
  you want to find which 3-in-a-row have the most stars total. The slow way
  is to slide the flashlight over and recount all 3 boxes from scratch every
  time. The clever way: when you slide one box to the right, you already
  know the old total - just subtract the stars in the box that went dark
  and add the stars in the new box that just lit up. Same answer, way less
  counting.
---
A sliding window keeps a running result (here, a sum) over a contiguous
chunk of the array and updates it incrementally as the chunk slides forward,
instead of recomputing it from scratch at every position. For a **fixed**
window size k, that turns an O(n·k) brute-force scan (recheck all k elements
every position) into a single O(n) pass.

```python
def max_window_sum(arr, k):
    window_sum = sum(arr[:k])
    best_sum = window_sum
    for end in range(k, len(arr)):
        start = end - k + 1
        window_sum += arr[end] - arr[start - 1]  # add new, drop old
        best_sum = max(best_sum, window_sum)
    return best_sum
```

The whole trick is that one line: `+= arr[end] - arr[start - 1]`. Each slide
does exactly two array reads and one addition, no matter how big k is -
compare that to summing all k elements fresh at every position.

This demo uses a **fixed-size** window (a constant k, "find the best
k-length chunk"). The same idea extends to a **variable-size** window (grow
until some condition breaks, then shrink) for problems like "smallest
subarray with sum at least X" - the window's size changes, but it's still
never fully rescanned.

**When to use it:** any "best/longest/smallest contiguous chunk of an array
or string" problem - subarray sums, longest substring without repeats,
maximum in every window of size k.
