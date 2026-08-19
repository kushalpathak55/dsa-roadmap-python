---
complexity:
  time_best: "O(n log n)"
  time_avg: "O(n log n)"
  time_worst: "O(n^2)"
  space: "O(log n)"
  stable: false
  in_place: true
eli5: >-
  Pick one kid from a messy line to be the "leader." Everyone shorter than
  the leader runs to stand on their left, everyone taller runs to stand on
  their right. Now the leader is standing exactly where they belong! Play
  the same game again separately with the left group and the right group,
  picking a new leader each time, until everyone in line is in order.
---
Quick sort picks a pivot, partitions the array so everything smaller than
the pivot ends up on its left and everything larger ends up on its right,
then recursively sorts each side. Unlike merge sort, the split is the hard
part and the two halves need no further combining.

```python
def quick_sort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = partition(arr, lo, hi)
        quick_sort(arr, lo, p - 1)
        quick_sort(arr, p + 1, hi)
    return arr

def partition(arr, lo, hi):
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

Its worst case (O(n²)) happens when the pivot is consistently the smallest
or largest element, e.g. an already-sorted array with last-element pivoting
- in practice, randomized or median-of-three pivot selection avoids this.
