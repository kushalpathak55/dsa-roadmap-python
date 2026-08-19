---
complexity:
  time_best: "O(V + E)"
  time_avg: "O(V + E)"
  time_worst: "O(V + E)"
  space: "O(V)"
eli5: >-
  Think about getting dressed: you have to put on socks before shoes, and
  a shirt before a jacket - some things MUST happen before others.
  Topological sort is like making a to-do list that respects every one of
  those "this must happen before that" rules, so you never end up trying
  to put your shoes on before your socks.
---
A topological sort orders the nodes of a **directed acyclic graph (DAG)** so
that every edge points from an earlier node to a later one - useful whenever
edges represent "must happen before" (course prerequisites, build/task
dependencies, spreadsheet formula evaluation order).

This demo uses **Kahn's algorithm**: repeatedly remove a node with no
remaining incoming edges (in-degree 0), and decrease its neighbors'
in-degrees accordingly - reusing the same queue-based approach as BFS.

```python
from collections import deque

def topological_sort(adjacency, in_degree):
    queue = deque(n for n in in_degree if in_degree[n] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) < len(in_degree):
        raise ValueError("graph has a cycle - no valid ordering exists")
    return order
```

**If the queue empties before every node is processed, the graph has a
cycle** - some nodes still have incoming edges from each other with no
"first" one to start from, so no valid ordering exists. That's a genuinely
useful side effect: Kahn's algorithm doubles as a cycle detector.

Edges are read left-to-right as "before": `A-B` means A must come before B.
The demo below computes every node's in-degree, then peels off in-degree-0
nodes one at a time, showing the resulting order (or the cycle, if one
exists).
