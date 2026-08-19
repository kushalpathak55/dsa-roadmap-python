---
complexity:
  time_best: "O(1)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(1)"
eli5: >-
  Imagine looking for your favorite toy in a big toy box, one item at a
  time, starting from the top. You pick up the first toy and ask "is this
  it?" If not, you put it down and pick up the next one - and the next,
  and the next - until you find it (or run out of toys and know it's not
  there). No shortcuts, no peeking ahead - just checking everyone, one by
  one, in order.
---
Linear search checks every element one by one, in order, until it finds the
target value or reaches the end of the array.

It makes no assumptions about the array's order, which is what makes it
universally applicable but also asymptotically slower than binary search on
sorted data.

```python
def linear_search(arr, target):
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1
```

**When to use it:** unsorted data, small arrays, or a one-off search where
sorting first wouldn't pay off.
