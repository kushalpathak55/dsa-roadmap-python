---
complexity:
  time_best: "O(1)"
  time_avg: "O(log n)"
  time_worst: "O(log n)"
  space: "O(1)"
eli5: >-
  Imagine a guessing game: a friend picks a number between 1 and 100 and
  will only say "higher" or "lower." The smart move is to guess 50 first -
  whatever they say, you just crossed out HALF of all the possible numbers
  in one guess! Keep guessing the middle of what's left, and you'll find
  it super fast - way faster than guessing 1, 2, 3... one at a time. The
  trick only works if the numbers are already lined up in order, like kids
  sorted from shortest to tallest.
---
Binary search exploits sorted order: it compares the target against the
middle element and discards half the remaining array each time, so the
search space shrinks exponentially instead of linearly.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

The visualization below sorts your input first, since binary search is only
correct on sorted data.

**When to use it:** sorted (or sortable-once, searched-many-times) data.
