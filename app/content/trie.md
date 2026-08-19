---
complexity:
  time_best: "O(L)"
  time_avg: "O(L)"
  time_worst: "O(L)"
  space: "O(N * L)"
  in_place: false
eli5: >-
  Imagine a family tree, but for words instead of people - and every letter
  gets its own box. "CAT" and "CAR" share the same first two boxes (C, then
  A), then split into separate boxes for T and R, because that's where the
  words stop being the same. Some boxes get a little flag on them meaning
  "a real word ends here!" - "CA" might just be a box you pass through with
  no flag, while "CAT" has one. That's how you can tell "just the beginning
  of some words" apart from "an actual whole word."
---
A trie (say "try", from re**trie**val) stores a set of strings by sharing
common prefixes: each node is one character, and a path from the root spells
out a prefix. Words that start the same way literally share the same nodes -
"cat" and "car" both walk through the same C -> A path before splitting.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

def insert(root, word):
    node = root
    for ch in word:
        node = node.children.setdefault(ch, TrieNode())
    node.is_word = True

def search(root, word):
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_word  # walked the whole word, but is it a COMPLETE one?
```

That last line is the whole point of a trie: reaching the end of "car"'s
letters only tells you `"car"` is a **prefix** something in the set starts
with - `is_word` is what tells you whether `"car"` is itself a complete
entry, not just a stepping stone to `"card"` or `"care"`. A hash set can
only answer "is this string in the set" - a trie can also answer "does
anything in the set *start with* this string," in the same O(L) time it
takes to walk the query's letters (L = the query's length), completely
independent of how many words are stored.

The demo below inserts each word letter by letter (reusing a branch
whenever one already exists), then searches three ways: the first word you
typed (a hit), that word with its last letter chopped off (a prefix that
usually isn't a complete word), and a string that shouldn't be there at all.

**When to use it:** autocomplete / typeahead, spell-checkers, IP routing
tables (longest-prefix match) - anything where "which stored strings share
this prefix" matters, not just exact-match lookup.
