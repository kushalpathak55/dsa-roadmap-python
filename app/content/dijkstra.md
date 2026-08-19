---
complexity:
  time_best: "O(V^2)"
  time_avg: "O((V + E) log V)"
  time_worst: "O((V + E) log V)"
  space: "O(V)"
eli5: >-
  Imagine you want the CHEAPEST way to get candy from your house to
  school, but some roads take more energy (steps) to walk than others.
  You always walk toward whichever nearby spot is currently cheapest to
  reach, and every time you arrive somewhere new, you check: "hey, is THIS
  a cheaper way to reach my other favorite spots?" Keep doing that, and
  eventually you know the cheapest path to everywhere.
---
Dijkstra's algorithm finds the shortest path from a start node to every
other node in a graph with non-negative edge weights. It repeatedly picks
the closest unvisited node, then **relaxes** each of its edges - updating a
neighbor's distance if reaching it through the current node is cheaper than
what's known so far.

```python
import heapq

def dijkstra(adjacency, start):
    dist = {start: 0}
    visited = set()
    pq = [(0, start)]
    while pq:
        d, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in adjacency[node]:
            candidate = d + weight
            if candidate < dist.get(neighbor, float('inf')):
                dist[neighbor] = candidate
                heapq.heappush(pq, (candidate, neighbor))
    return dist
```

A real implementation uses a **min-heap** (priority queue) to fetch the
closest unvisited node in O(log V) instead of scanning every node - that's
where the `(V + E) log V` complexity comes from. The demo below uses a
plain linear scan to pick the minimum each round instead (O(V²) overall,
the "simplest first cut"), since it's easier to follow step by step at this
scale; the *order* of operations - select closest, relax its edges - is
identical either way.

**Why it needs non-negative weights:** the algorithm assumes once a node is
visited, its shortest distance is final - a negative edge discovered later
could still improve it, which breaks that assumption. (Bellman-Ford handles
negative weights, at the cost of being slower.)

The demo below runs Dijkstra from your chosen start node, narrating each
relaxation and updating every node's running distance.
