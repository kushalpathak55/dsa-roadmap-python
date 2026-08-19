---
complexity:
  time_best: "O(n^2)"
  time_avg: "O(n^2)"
  time_worst: "O(n^2)"
  space: "O(1)"
  stable: false
  in_place: true
eli5: >-
  You have a messy pile of toy cars and want to line them up from smallest
  to biggest. Each round, you dig through the WHOLE pile to find the
  smallest car, then place it at the end of your neat line. Then you look
  through what's left to find the next smallest, and the next - always
  picking the best one you can find right now, one at a time, until the
  pile is empty and your line is perfect.
---
Selection sort divides the array into a sorted prefix and an unsorted
remainder. On each pass, it scans the remainder for the minimum element and
swaps it into place at the end of the sorted prefix.

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

Unlike bubble sort, it makes exactly one swap per pass, so it minimizes
writes at the cost of always scanning the full remainder even if the array
is already sorted.
