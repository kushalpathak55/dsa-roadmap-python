---
complexity:
  time_best: "O(n log n)"
  time_avg: "O(n log n)"
  time_worst: "O(n log n)"
  space: "O(1)"
  stable: false
  in_place: true
eli5: >-
  Remember the family tree where the tallest grown-up always ends up at the
  top, so you can find them instantly? Heap sort keeps grabbing that
  tallest person from the top, moves them to the back of a brand new line
  (building it from the end backwards), then lets the next-tallest person
  bubble up to the top and grabs them too - over and over, until the new
  line reads shortest to tallest, left to right.
---
Heap sort gets `O(n log n)` worst-case time - better than the other simple
`O(n^2)` sorts - by first turning the array into a
[binary heap](/topic/binary-heap), then repeatedly pulling the maximum off
the top.

```python
def heap_sort(arr):
    n = len(arr)

    def sift_down(heap_size, root):
        while True:
            largest, left, right = root, 2 * root + 1, 2 * root + 2
            if left < heap_size and arr[left] > arr[largest]:
                largest = left
            if right < heap_size and arr[right] > arr[largest]:
                largest = right
            if largest == root:
                break
            arr[root], arr[largest] = arr[largest], arr[root]
            root = largest

    # Build a max-heap: sift down every non-leaf node, root last.
    for i in range(n // 2 - 1, -1, -1):
        sift_down(n, i)

    # Repeatedly move the max (the root) to the end, then re-heapify what's left.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sift_down(end, 0)

    return arr
```

Because a binary heap is just an array read as an implicit tree (a node at
index `i` has children at `2i+1` and `2i+2`), heap sort needs **no extra
array** - unlike merge sort's `O(n)` auxiliary buffer, it sorts in place
with `O(1)` extra space, while still guaranteeing `O(n log n)` even in the
worst case (unlike quick sort, which can degrade to `O(n^2)`).

The trade-off: heap sort is **not stable** (equal elements can end up
reordered relative to each other, since sifting swaps across the whole
heap rather than shifting neighbors), and in practice it's usually a bit
slower than a well-tuned quick sort due to worse cache locality - jumping
between `arr[i]`, `arr[2i+1]`, and `arr[2i+2]` touches memory less
predictably than quick sort's mostly-sequential scans.

The demo below builds the max-heap first (watch the array take on heap
shape even though it's still drawn as flat bars), then repeatedly extracts
the maximum to the end.
