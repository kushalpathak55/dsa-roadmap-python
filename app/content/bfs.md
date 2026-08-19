---
complexity:
  time_best: "O(V + E)"
  time_avg: "O(V + E)"
  time_worst: "O(V + E)"
  space: "O(V)"
eli5: >-
  Imagine dropping a pebble into a pond and watching the ripples spread
  out in circles - first the closest water, then a little further, then
  further still. Breadth-first search visits your closest friends first,
  then your friends' friends, then THEIR friends, spreading outward one
  ring at a time - so you never skip ahead to someone far away before
  checking everyone closer.
---
Breadth-first search explores a graph level by level: visit the start node,
then all of its neighbors, then all of *their* unvisited neighbors, and so
on - using a **queue** to always process the oldest-discovered node next.

```python
from collections import deque

def bfs(adjacency, start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adjacency[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
```

Marking a node visited **at enqueue time** (not when it's dequeued) is the
detail that keeps a node from being queued twice through two different
neighbors. Because it expands outward one full "ring" at a time, BFS is also
the standard way to find the shortest path in an unweighted graph - the
first time you reach a node is guaranteed to be via a shortest path.

The demo below runs BFS from your chosen start node, showing the queue's
contents at every step. Edges the search actually explores through are
highlighted as the BFS tree.
