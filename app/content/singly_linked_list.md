---
complexity:
  time_best: "O(1)"
  time_avg: "O(n)"
  time_worst: "O(n)"
  space: "O(n)"
eli5: >-
  Imagine a treasure hunt where each clue tells you where to find the NEXT
  clue, instead of a map showing everything at once. You start at clue
  one, read it, and it points you to clue two, which points to clue
  three, and so on, until the last clue says "The End!" To sneak in a new
  clue, you don't have to redo the whole hunt - you just tell the clue
  before it to point somewhere new.
---
A singly linked list is a chain of nodes where each node holds a value and a
pointer to the next node. Unlike an array, its elements aren't stored
contiguously in memory, so insertion and deletion don't require shifting
anything - just relinking a couple of pointers.

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

def append(head, value):
    node = Node(value)
    if head is None:
        return node
    current = head
    while current.next:
        current = current.next
    current.next = node
    return head

def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev
```

The trade-off versus an array: O(1) insertion/deletion once you're at the
right spot, but O(n) just to *get* to that spot (no random access, and no
`arr[i]`) - and each node costs extra memory for the pointer.

The demo below builds a list from your input, traverses it, appends a new
value, deletes the first element, then reverses the whole list.
