"""Shared helpers for building step dicts. Every step carries the common envelope
(step_index, kind, note, counters) plus family-specific fields, per the array-family schema.
"""

from __future__ import annotations

from typing import Any

MAX_ARRAY_SIZE = 60
MAX_LIST_SIZE = 20
MAX_TREE_SIZE = 15
MAX_GRAPH_NODES = 15
MAX_GRAPH_EDGES = 30
MAX_FIB_N = 25
MAX_KNAPSACK_ITEMS = 8
MAX_KNAPSACK_CAPACITY = 20
MAX_STRING_LEN = 12
MAX_TRIE_WORDS = 8
MAX_TRIE_WORD_LEN = 10
MAX_N_QUEENS = 5  # step count grows ~4x per n (96 steps at n=4, 338 at n=5, 1200+ at n=6)


def predict_prompt(question: str, options: list[Any], answer: Any) -> dict[str, Any]:
    """A step's optional 'guess what happens next' prompt. `options` and
    `answer` are coerced to strings since the frontend just does an exact
    string match against whichever button was clicked - keeps the
    predict-mode gate in JS completely generic across every step family.
    """
    return {
        "question": question,
        "options": [str(o) for o in options],
        "answer": str(answer),
    }


def array_step(
    *,
    step_index: int,
    kind: str,
    array: list[int],
    note: str = "",
    compare: list[int] | None = None,
    swap: list[int] | None = None,
    pivot: list[int] | None = None,
    sorted_indices: list[int] | None = None,
    range_: list[int] | None = None,
    found: int | None = None,
    counters: dict[str, int] | None = None,
    predict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "step_index": step_index,
        "kind": kind,
        "array": list(array),
        "indices": {
            "compare": compare or [],
            "swap": swap or [],
            "pivot": pivot or [],
            "sorted": sorted_indices or [],
            "range": range_ or [],
            "found": found,
        },
        "note": note,
        "counters": counters or {},
        "predict": predict,
    }


def tree_step(
    *,
    step_index: int,
    kind: str,
    nodes: list[dict[str, Any]],
    note: str = "",
    focus: dict[str, Any] | None = None,
    counters: dict[str, int] | None = None,
    predict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Step schema for the node-link family (trees/heaps - see graphs later).

    Each node is {"id", "value", "state", "parent": id|None} - the D3 renderer
    builds the hierarchy straight from `parent` (d3.stratify), so no separate
    edges list is needed for a tree. Layout is recomputed fresh every step
    (unlike graphs, a tree's shape legitimately changes step to step, and
    D3's tree layout is a pure function of that shape - no jitter risk).
    `focus` is a free-form bag for algorithm-specific side state (e.g. a
    traversal's visit order so far, or a target value being searched for).
    """
    return {
        "step_index": step_index,
        "kind": kind,
        "nodes": [dict(n) for n in nodes],
        "focus": focus or {},
        "note": note,
        "counters": counters or {},
        "predict": predict,
    }


def graph_step(
    *,
    step_index: int,
    kind: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    note: str = "",
    focus: dict[str, Any] | None = None,
    counters: dict[str, int] | None = None,
    predict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Step schema for graphs. Unlike a tree, a node can have multiple parents
    or none, so edges are listed explicitly: {"source", "target", "directed", "state"}.

    Critical difference from the tree family: each node's `x`/`y` is computed
    ONCE before the algorithm runs (see graphs.py:circular_layout) and then
    baked into every step unchanged - recomputing layout per step (like a live
    force simulation) would make nodes jitter every time state changes, which
    is disorienting. Only `state` varies step to step, never position.
    """
    return {
        "step_index": step_index,
        "kind": kind,
        "nodes": [dict(n) for n in nodes],
        "edges": [dict(e) for e in edges],
        "focus": focus or {},
        "note": note,
        "counters": counters or {},
        "predict": predict,
    }


def dp_step(
    *,
    step_index: int,
    kind: str,
    grid: list[list[Any]],
    note: str = "",
    cursor: dict[str, int] | None = None,
    highlight_cells: list[tuple[int, int]] | None = None,
    row_labels: list[str] | None = None,
    col_labels: list[str] | None = None,
    counters: dict[str, int] | None = None,
    predict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Step schema for dynamic-programming grids. Always 2D, even for a 1D
    table like fibonacci (rendered as a single row) - one dp_grid.js renderer
    then covers every DP topic without a "1D special case". A grid cell is
    `None` until computed (renders as empty), otherwise a value.
    """
    return {
        "step_index": step_index,
        "kind": kind,
        "grid": [list(row) for row in grid],
        "row_labels": list(row_labels or []),
        "col_labels": list(col_labels or []),
        "cursor": cursor,
        "highlight": {"cells": [list(c) for c in (highlight_cells or [])]},
        "note": note,
        "counters": counters or {},
        "predict": predict,
    }


def list_step(
    *,
    step_index: int,
    kind: str,
    layout: str,
    nodes: list[dict[str, Any]],
    note: str = "",
    pointers: dict[str, str | None] | None = None,
    counters: dict[str, int] | None = None,
    predict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Step schema for the linear DOM-box family (linked list / stack / queue).

    layout selects how the renderer arranges the boxes: "chain" (linked list -
    horizontal, arrows between nodes, head/tail/current pointers), "stack"
    (vertical, grows upward, top pointer), or "queue" (horizontal, no arrows,
    front/rear pointers). Node state drives box color: default/active/new/removed/target.
    """
    return {
        "step_index": step_index,
        "kind": kind,
        "layout": layout,
        "nodes": [dict(n) for n in nodes],
        "pointers": pointers or {},
        "note": note,
        "counters": counters or {},
        "predict": predict,
    }
