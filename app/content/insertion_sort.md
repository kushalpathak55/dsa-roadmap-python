---
complexity:
  time_best: "O(n)"
  time_avg: "O(n^2)"
  time_worst: "O(n^2)"
  space: "O(1)"
  stable: true
  in_place: true
eli5: >-
  Think about holding a hand of playing cards. You start with one card,
  then pick up the next one and slide it into the exact right spot among
  the cards you're already holding - not just at the end, but exactly
  where it belongs, like slipping a book onto a shelf where it fits
  alphabetically. Do that for every new card, one at a time, and your
  whole hand ends up perfectly sorted.
---
Insertion sort builds a sorted prefix one element at a time: it takes the
next unsorted element and shifts it left past every already-sorted element
that's bigger than it, until it lands in the right spot.

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

It's the fastest of the simple O(n²) sorts on nearly-sorted data (best case
is O(n), a single pass with no shifts), which is why it's often used as the
base case inside hybrid sorts like Timsort.
