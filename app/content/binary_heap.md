---
complexity:
  time_best: "O(1)"
  time_avg: "O(log n)"
  time_worst: "O(log n)"
  space: "O(n)"
eli5: >-
  Imagine a family tree with one strict rule: every grown-up MUST be
  smaller (or equal) than their kids, no exceptions! That means the very
  smallest person in the whole family is always standing right at the top
  - so you can find them instantly, no searching needed. When someone new
  joins at the bottom, they keep swapping places with their parent until
  the rule is true again, like a game of "whoever's smallest keeps moving
  up."
---
A binary heap is a *complete* binary tree (every level full except possibly
the last, filled left to right) that satisfies the **heap property**: in a
min-heap, every parent is smaller than or equal to both its children - so
the minimum is always at the root, reachable in O(1).

Because the tree is always complete, it can be stored compactly in a plain
array with no pointers at all - for a node at index `i`, its parent is at
`(i-1)//2` and its children are at `2i+1` and `2i+2`.

```python
def push(heap, value):
    heap.append(value)
    i = len(heap) - 1
    while i > 0 and heap[i] < heap[(i - 1) // 2]:
        parent = (i - 1) // 2
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent

def pop_min(heap):
    heap[0], heap[-1] = heap[-1], heap[0]
    minimum = heap.pop()
    i, n = 0, len(heap)
    while True:
        left, right, smallest = 2 * i + 1, 2 * i + 2, i
        if left < n and heap[left] < heap[smallest]: smallest = left
        if right < n and heap[right] < heap[smallest]: smallest = right
        if smallest == i: break
        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest
    return minimum
```

Insert appends at the next open leaf then **sifts up** while it's smaller
than its parent; extracting the min swaps the root with the last leaf, pops
that leaf off, then **sifts down** from the root. Both operations only ever
walk one root-to-leaf path, which is why they're O(log n) even though a full
scan of the array would be O(n).

**Where it shows up:** priority queues, heap sort, and Dijkstra's algorithm's
"always process the closest unvisited node next" step.

The demo below inserts each of your input values (sifting up as needed),
then extracts the minimum a few times (sifting down to repair the heap).
