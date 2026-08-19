---
complexity:
  time_best: "O(V + E)"
  time_avg: "O(V + E)"
  time_worst: "O(V + E)"
  space: "O(V)"
eli5: >-
  Imagine exploring a maze by picking one path and following it as far as
  you possibly can - turn after turn - until you hit a dead end. Only THEN
  do you turn around and try the next path you skipped. You commit fully
  to one direction before ever backtracking, like reading one whole
  hallway of a haunted house before trying the next door.
---
Depth-first search explores as far as possible down one path before
backtracking - using a **stack** (either explicit, or implicit via
recursion/the call stack) instead of BFS's queue.

```python
def dfs(adjacency, start):
    visited = set()
    order = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in adjacency[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return order
```

Same graph, same starting point, but a completely different visit order
than BFS - DFS commits to one branch and follows it to the end before
trying another. It's the basis for cycle detection, topological sorting,
and finding connected components.

The demo below runs DFS from your chosen start node, showing the stack's
contents at every step. Compare its visit order (and the shape of the
resulting tree) against BFS on the same graph.
