---
complexity:
  time_best: "O(1)"
  time_avg: "O(1)"
  time_worst: "O(n)"
  space: "O(n)"
eli5: >-
  Imagine a wall of numbered cubbies at school, like a locker room. To
  pick which cubby is yours, you do a little math trick with your name
  (like counting its letters) that always lands on the SAME cubby number
  every time you do it. If two friends' names land on the same cubby,
  that's okay - you both hang your backpacks on the same hook and just
  check the name tag to know whose is whose.
---
A hash table maps keys to array indices via a **hash function**, giving
average O(1) insert/lookup/delete - no scanning required. The catch: two
different keys can hash to the same index (a **collision**), so a
real implementation needs a strategy for handling that.

This visualization uses **separate chaining**: each bucket holds a small
linked list, and colliding keys just get appended to that bucket's chain.

```python
class HashTable:
    def __init__(self, size=7):
        self.buckets = [[] for _ in range(size)]

    def insert(self, key):
        index = key % len(self.buckets)
        self.buckets[index].append(key)  # append even if the bucket isn't empty
```

With a good hash function and a reasonable load factor (items per bucket),
chains stay short and operations stay close to O(1) - but a bad hash
function (or too many items for too few buckets) degrades every operation
toward O(n), since you'd have to walk one long chain.

The demo below hashes each of your input values with `value % 7` and inserts
it into the corresponding bucket, chaining onto any bucket that already has
an item.
