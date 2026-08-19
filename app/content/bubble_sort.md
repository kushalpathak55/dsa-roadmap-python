---
complexity:
  time_best: "O(n)"
  time_avg: "O(n^2)"
  time_worst: "O(n^2)"
  space: "O(1)"
  stable: true
  in_place: true
eli5: >-
  Picture a row of kids lined up by height, but all mixed up. You walk down
  the line comparing each pair of neighbors - if the shorter kid is
  standing in front of the taller one, you ask them to swap! You keep
  walking up and down the line swapping neighbors until nobody needs to
  swap anymore. The tallest kid slowly "bubbles" to the end, like a bubble
  floating up through soda - that's exactly where the name comes from.
---
Bubble sort repeatedly walks the array, swapping adjacent elements that are
out of order. Each full pass "bubbles" the largest remaining element up to
its final position, so the pass length shrinks by one each time.

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
```

It's rarely used in practice (insertion sort dominates it at the same
complexity class), but it's the simplest possible illustration of
comparison-based sorting.
