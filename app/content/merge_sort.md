---
complexity:
  time_best: "O(n log n)"
  time_avg: "O(n log n)"
  time_worst: "O(n log n)"
  space: "O(n)"
  stable: true
  in_place: false
eli5: >-
  You have a huge pile of mixed-up puzzle pieces, so you ask friends to
  help. Split the pile in half, then split those halves in half again, and
  again, until every tiny pile has just ONE piece (which is already
  "sorted" all by itself!). Now put pairs of tiny piles back together in
  order, then bigger piles, then bigger - until the whole pile is neatly
  sorted again. Break the big problem into tiny easy ones, then zip them
  back together!
---
Merge sort splits the array in half recursively until each piece has one
element, then merges pairs of already-sorted pieces back together in
order. The split is trivial; all the work happens in the merge step.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]
```

Because it always splits evenly, its worst case matches its best case -
O(n log n) no matter the input - at the cost of O(n) auxiliary space for
the merge buffers.
