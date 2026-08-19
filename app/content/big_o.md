---
eli5: >-
  Imagine folding laundry. If you fold one shirt at a time, a pile twice as
  big takes you twice as long - that's steady, predictable growth. Now
  imagine a magic trick that lets you fold the WHOLE pile in one flip, no
  matter how big it is - twice as much laundry, same amount of time! And
  imagine a much worse way: for every shirt, you first compare it against
  every OTHER shirt in the pile before folding it - double the laundry and
  suddenly it's four times the work, not two. Big-O is just a name for
  which of these three stories describes how your work grows as the pile
  grows.
---
Big-O notation describes how an algorithm's running time (or memory use)
grows as the input size `n` grows - not the exact number of operations,
just the *shape* of the growth curve. It answers "if I double the input,
roughly how much more work am I doing?" rather than "exactly how many
milliseconds will this take?" (that depends on your CPU, not the algorithm).

```python
def constant(arr):        # O(1) - same work regardless of len(arr)
    return arr[0] if arr else None

def linear(arr):          # O(n) - work grows directly with len(arr)
    total = 0
    for x in arr:
        total += x
    return total

def quadratic(arr):       # O(n^2) - work grows with the SQUARE of len(arr)
    pairs = []
    for x in arr:
        for y in arr:
            pairs.append((x, y))
    return pairs
```

## The common growth rates, fastest to slowest

| Notation | Name | Example from this app |
|---|---|---|
| `O(1)` | constant | hash table lookup, array index access |
| `O(log n)` | logarithmic | binary search - each step halves the remaining space |
| `O(n)` | linear | linear search, traversing a linked list |
| `O(n log n)` | linearithmic | merge sort, quick sort (average case) |
| `O(n^2)` | quadratic | bubble sort, selection sort, insertion sort |
| `O(2^n)` | exponential | trying every subset (the brute-force knapsack) |

## A few things Big-O deliberately ignores

**Constants and lower-order terms get dropped.** An algorithm that does
`3n + 100` operations is still `O(n)` - as `n` gets large, the `3` and the
`100` stop mattering compared to the growth of `n` itself. This is *why*
Big-O is useful: it lets you compare algorithms' fundamental behavior
without getting lost in implementation-specific constants.

**Best, average, and worst case are different questions.** Quick sort is
`O(n log n)` on average but `O(n^2)` in the worst case (an already-sorted
array with a badly chosen pivot) - that's why every complexity table in
this app lists all three separately, alongside the space (memory) the
algorithm needs on top of its input.

**A smaller Big-O isn't automatically faster in practice.** For small `n`,
an `O(n^2)` algorithm with a tiny constant factor can easily beat an
`O(n log n)` one with a large constant factor - insertion sort, for
example, is often faster than more "efficient" sorts on small or
nearly-sorted arrays. Big-O tells you how things change as `n` grows large,
not which one wins for the input in front of you today.

Every topic in this app that has a live demo also has a complexity table -
now that you know what those columns mean, go watch one in action.
