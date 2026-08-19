---
complexity:
  time_best: "O(n)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(1)"
eli5: >-
  Imagine you and a friend stand at opposite ends of a long table of snacks
  with price tags, and you're looking for two snacks that together cost
  EXACTLY $10. You start at the cheapest end, your friend starts at the
  priciest end. Add your two prices together: too cheap? You step toward
  the middle to a pricier snack. Too expensive? Your friend steps toward a
  cheaper one. You only ever walk toward each other, never backward - so
  you're guaranteed to meet in the middle having checked every useful pair,
  without ever comparing every snack to every other snack.
---
Two pointers is a technique, not a single algorithm: walk two indices toward
each other (or in the same direction) through a **sorted** array, using the
comparison at each step to decide which pointer moves. Because both pointers
only ever move inward and never revisit ground, the whole scan is a single
O(n) pass - one pointer's worth of movement 'pays for' the other's, instead
of checking every pair with a nested loop.

```python
def two_pointer_sum(arr, target):
    arr = sorted(arr)
    left, right = 0, len(arr) - 1
    while left < right:
        total = arr[left] + arr[right]
        if total == target:
            return left, right
        if total < target:
            left += 1   # only way to grow the sum
        else:
            right -= 1  # only way to shrink the sum
    return None
```

The key insight is the direction argument: if the current pair sums too
small, the *only* way to increase the total is to move the left pointer to a
bigger value (the right pointer is already at the biggest value left in
range) - so there's never a need to try moving the other pointer instead.
That's what turns an O(n²) check-every-pair search into O(n).

The demo below sorts your input first (two pointers requires sorted data,
the same precondition as binary search), then walks the pointers inward
until it finds a pair or they cross.

**When to use it:** searching for a pair (or a window) in sorted data based
on a running sum or difference - pair-sum problems, removing duplicates in
place, merging two sorted arrays.
