---
complexity:
  time_best: "O(1)"
  time_avg: "O(1)"
  time_worst: "O(1)"
  space: "O(n)"
eli5: >-
  Think about waiting in line for ice cream. New friends join at the BACK
  of the line, and whoever has been waiting longest, at the FRONT, gets
  served first. Nobody gets to cut in the middle - it's always "first
  come, first served," which is why it's called "First In, First Out."
---
A queue is First-In-First-Out (FIFO): elements are added at the rear
("enqueue") and removed from the front ("dequeue") - like a line of people
at a checkout counter.

```python
from collections import deque

queue = deque()
queue.append(5)        # enqueue
queue.append(3)        # enqueue
front = queue[0]        # peek -> 5
queue.popleft()          # dequeue -> 5
```

Python's `list` supports the same operations, but `pop(0)` on a list is
O(n) because everything has to shift left - `collections.deque` is the
right structure since it's O(1) at both ends.

**Where it shows up:** breadth-first search, task scheduling, print/request
queues - anywhere "first come, first served" order matters.

The demo below enqueues each of your input values in order, then dequeues
about half of them.
