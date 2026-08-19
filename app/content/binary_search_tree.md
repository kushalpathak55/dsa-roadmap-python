---
complexity:
  time_best: "O(log n)"
  time_avg: "O(log n)"
  time_worst: "O(n)"
  space: "O(n)"
eli5: >-
  Imagine a family-tree guessing game: every grown-up can have at most two
  kids standing below them - the SMALLER-numbered kid always stands on the
  left, the BIGGER-numbered kid always stands on the right. Looking for
  someone? Start at the top and go left or right depending on whether
  your number is smaller or bigger than the person in front of you - just
  like the "higher or lower" guessing game, except now it's a family tree
  instead of a straight line!
---
A binary search tree (BST) keeps every node's left subtree smaller and right
subtree larger, so a search can discard half the remaining tree at each
step - the same idea as binary search, but on a linked structure instead of
a sorted array.

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def insert(node, value):
    if node is None:
        return Node(value)
    if value < node.value:
        node.left = insert(node.left, value)
    elif value > node.value:
        node.right = insert(node.right, value)
    return node

def search(node, value):
    if node is None or node.value == value:
        return node
    return search(node.left, value) if value < node.value else search(node.right, value)
```

The O(log n) average case assumes the tree stays roughly balanced. Insert
values in sorted order, though, and it degenerates into a straight chain -
O(n) per operation, no better than a linked list. (Self-balancing variants
like AVL and red-black trees exist specifically to prevent this.)

**Deleting** a node has three cases: a leaf is just removed; a node with one
child is replaced by that child; a node with two children is replaced by its
in-order successor (the smallest value in its right subtree), which is then
removed from its original spot.

The demo below builds a tree from your input, searches for the target,
and deletes it, narrating which of the three cases applies.
