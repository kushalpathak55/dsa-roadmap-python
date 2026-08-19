---
complexity:
  time_best: "O(1)"
  time_avg: "O(1)"
  time_worst: "O(1)"
  space: "O(n)"
eli5: >-
  Think of a stack of pancakes. You can only add a new pancake to the TOP,
  and you can only eat the one that's on top too - you can't grab one from
  the middle without knocking the others over! The last pancake you put on
  is always the first one you take off. That's why grown-ups call it
  "Last In, First Out."
---
A stack is Last-In-First-Out (LIFO): you can only add ("push") or remove
("pop") from one end, the top. Think of a stack of plates - you take from
the top, not the bottom.

```python
stack = []
stack.append(5)   # push
stack.append(3)   # push
top = stack[-1]   # peek -> 3
stack.pop()        # pop -> 3
```

Because both operations only ever touch the top, they're O(1) regardless of
how many elements are underneath.

**Where it shows up:** function call stacks (recursion), undo/redo history,
matching balanced brackets `()[]{}` (push an opening bracket, pop and check
on a closing one), and depth-first search.

The demo below pushes each of your input values in order, then pops about
half of them back off.
