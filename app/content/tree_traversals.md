---
complexity:
  time_best: "O(n)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(h)"
eli5: >-
  It's like visiting every house in a family tree, but you get to pick the
  order: knock on the grandparent's door first and work down (preorder),
  visit the smallest kid, then the parent, then the biggest kid - like
  reading left to right (inorder), visit all the kids before the parent
  (postorder), or visit everyone floor-by-floor like walking through each
  level of a building (level-order). Same houses, four different orders to
  knock on the doors!
---
Visiting every node in a tree can be done in more than one order, and each
order is useful for a different purpose. `h` in the space column is the
tree's height - that's the depth of the recursion (or explicit stack/queue).

```python
def inorder(node):    # left, self, right - sorted order on a BST
    if node:
        yield from inorder(node.left)
        yield node.value
        yield from inorder(node.right)

def preorder(node):   # self, left, right - useful for copying a tree
    if node:
        yield node.value
        yield from preorder(node.left)
        yield from preorder(node.right)

def postorder(node):  # left, right, self - useful for deleting a tree
    if node:
        yield from postorder(node.left)
        yield from postorder(node.right)
        yield node.value

from collections import deque

def level_order(root):  # breadth-first, level by level
    queue = deque([root] if root else [])
    while queue:
        node = queue.popleft()
        yield node.value
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)
```

The first three are depth-first (they use the call stack) and differ only in
*when* a node is visited relative to its children. **In-order traversal of a
BST always visits values in sorted order** - a handy way to sanity-check
that a tree is a valid BST. Level-order is breadth-first and needs an
explicit queue instead of recursion.

The demo below builds a tree from your input, then runs all four traversals
in sequence, highlighting each node as it's visited.
