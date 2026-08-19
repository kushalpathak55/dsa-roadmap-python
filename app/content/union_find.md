---
complexity:
  time_best: "O(α(n))"
  time_avg: "O(α(n))"
  time_worst: "O(α(n))"
  space: "O(n)"
eli5: >-
  Imagine everyone in a huge room starts as their own tiny friend group of
  one. Every time two people become friends, their whole friend group
  merges into one bigger group - and to keep things fast, the SMALLER group
  always joins onto the BIGGER one, like a small crowd walking over to join
  a bigger crowd instead of the other way around. To check "are these two
  people in the same friend group," you just trace each one back to their
  group's one designated leader - and while you're at it, you grab everyone
  you passed and point them straight at that leader, so next time it's an
  instant answer instead of a long walk.
---
Union-Find (a.k.a. Disjoint Set Union) answers one question extremely fast,
over and over: "are these two elements in the same set?" Each set is a tree
of parent pointers - not for ordering (like a BST), just for tracking group
membership - and a set's "identity" is whichever element is its own parent
(its root).

```python
def find(parent, x):
    root = x
    while parent[root] != root:
        root = parent[root]
    while parent[x] != root:       # path compression
        parent[x], x = root, parent[x]
    return root

def union(parent, rank, x, y):
    root_x, root_y = find(parent, x), find(parent, y)
    if root_x == root_y:
        return
    if rank[root_x] < rank[root_y]:
        root_x, root_y = root_y, root_x
    parent[root_y] = root_x        # union by rank
    if rank[root_x] == rank[root_y]:
        rank[root_x] += 1
```

Two optimizations, stacked, are what get `find` and `union` down to
essentially O(1) each (formally O(α(n)), where α is the inverse Ackermann
function - it's under 5 for any n you could ever construct in practice):

- **Union by rank**: always attach the shorter tree under the taller one's
  root, never the reverse - this alone caps tree height at O(log n).
- **Path compression**: every `find` call flattens the path it just walked,
  pointing every node it passed straight at the root - so the *next* lookup
  for any of them is instant.

The demo below processes your union operations one at a time. Each one runs
two `find` calls (walking - and often compressing - a path to each side's
root) before deciding whether a union even needs to happen, and if so, which
root wins based on the union-by-rank rule above.

**When to use it:** tracking connected components as edges are added
incrementally - Kruskal's minimum spanning tree algorithm, cycle detection
in an undirected graph, "are these two accounts linked" style queries.
