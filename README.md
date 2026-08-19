# dsa-roadmap-python

An interactive app for learning Data Structures & Algorithms: concept explanations,
complexity analysis, step-by-step algorithm visualizations (play/pause/step/scrub),
a "predict what happens next" quiz mode, and progress tracking - covering the full
standard DSA interview roadmap, 28 topics across 12 categories.

## Run it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000.

## Test

```bash
pytest
```

## What's here

The roadmap is fully built - every topic has a written explanation, an ELI5
analogy, and (except for the one purely conceptual page, Big-O Notation) a
live interactive visualizer:

- **Foundations**: Big-O Notation (concept page, no visualizer).
- **Arrays & Searching**: Linear Search, Binary Search.
- **Array Techniques**: Two Pointers, Sliding Window.
- **Sorting**: Bubble, Selection, Insertion, Merge, Quick, Heap Sort.
- **Linked Lists**: Singly Linked List (build/traverse/insert/delete/reverse).
- **Stacks & Queues**: Stack (push/pop), Queue (enqueue/dequeue).
- **Hashing**: Hash Table with separate chaining.
- **Trees**: Binary Search Tree, Tree Traversals (all four orders), Trie
  (prefix tree), Union-Find (disjoint set, path compression + union by rank).
- **Heaps**: Binary Heap (min-heap insert/extract).
- **Graphs**: BFS, DFS, Dijkstra's Algorithm, Topological Sort (Kahn's).
- **Dynamic Programming**: Fibonacci (Memoization), 0/1 Knapsack, Longest
  Common Subsequence.
- **Backtracking**: N-Queens (finds every solution, so it backtracks even
  after completing a board).

### Predict Mode

Every visualizer can be flipped into a quiz: playback pauses right before
each meaningful decision (a comparison, a branch, a placement) and asks you
to guess the outcome before revealing it. Available across every algorithm
family - array, tree, graph, DP, linked-list/stack/queue, and hash table.

### Progress tracking

A topic is marked complete once its visualizer plays through to the end (or,
for the one concept-only page, as soon as it's read). Tracked entirely
client-side in `localStorage` - no accounts, nothing sent to a server. Shows
up as checkmarks in the sidebar, a per-category count on the home page, and
an overall progress bar.

### Command palette

`Ctrl+K` (or `⌘K`) opens a fuzzy quick-jump across all 28 topics, built from
the same nav data the sidebar renders - no separate index to keep in sync.

### Keyboard shortcuts

Inside any visualizer: `Space` play/pause, `←`/`→` step back/forward, `Home`
reset.

## Architecture

Each algorithm is a Python generator that yields full-state-snapshot "step"
dicts (never diffs), which is what makes scrubbing/stepping trivial - the
frontend just renders `steps[i]`, it never re-derives algorithm logic. A
shared JS `StepPlayer` (play/pause/step/scrub/speed) pairs with one renderer
per step family:

- **array** - Canvas bar chart (`bars.js`).
- **list** - DOM boxes + arrows, shared by linked list/stack/queue (`list_boxes.js`).
- **hash** - bucket rows reusing the DOM-box renderer (`hash_table.js`).
- **tree** - D3 tree layout; supports a *forest* of disjoint trees for
  Union-Find, not just a single root (`tree_graph.js`).
- **graph** - D3 with a frozen circular layout (positions computed once in
  Python and baked into every step, so nodes never jitter) and directed-edge
  arrowheads (`tree_graph.js`).
- **dp** - an HTML table, reused as a plain grid for N-Queens' board
  (`dp_grid.js`).

See `app/algorithms/` (generators + step schemas), `app/content/topics.yaml`
(the single source of truth for the nav/roadmap), and `app/static/js/` for
the full architecture - adding a topic to an existing family is just "write
the generator," no new UI plumbing required.

## Design

A dark, IDE/debugger-inspired visual identity (single committed theme, no
light/dark toggle) - monospace chrome, a file-tree-style sidebar, breadcrumbs,
and `// comment`-style section labels. Design tokens live in
`app/static/css/style.css`.

## Accessibility

Skip-to-content link, semantic landmarks, `aria-current` on the active nav
item, and a full ARIA combobox/listbox pattern for the command palette
(focus trap while open, focus restored to whatever opened it on close). The
predict-mode panel is a live region so questions and feedback are announced;
step narration is live only while paused/stepping manually, not during fast
autoplay. Progress checkmarks (CSS-generated, not reliably announced by
screen readers) have a real text alternative. Motion respects
`prefers-reduced-motion`.

## Mobile / iOS

Responsive and installable as a home-screen web app:
- Sidebar nav collapses to a scrollable top bar below 780px; inputs and buttons meet
  the 44pt touch-target minimum; form inputs are 16px to avoid iOS's zoom-on-focus.
- The Canvas bar renderer is devicePixelRatio-aware (crisp on Retina screens) and
  repaints on resize/orientation change.
- `manifest.json` + `apple-touch-icon` + `theme-color`/`apple-mobile-web-app-*` meta
  tags support "Add to Home Screen" with a standalone display mode.
- Verified with Playwright under WebKit (Safari's engine) using an iPhone 13 device
  profile: no horizontal overflow, no console errors, correct canvas scaling in both
  orientations.
