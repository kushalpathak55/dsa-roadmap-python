"""Disjoint Set (Union-Find) with union-by-rank and path compression. Input
reuses the graph family's "A-B" edge text format - each token means
"union these two elements" - but the RESULT is rendered as a forest (a tree
per surviving set, via the tree-family step schema), not a graph, since
what's interesting here is the parent-pointer structure, not fixed positions.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from typing import Any

from app.algorithms.common import predict_prompt, tree_step
from app.algorithms.graphs import ordered_node_ids, parse_edges


def _root_of(parent: dict[str, str], x: str) -> str:
    """Pure lookup (no path compression) - used only for the set-count
    counter, so counting never mutates state the visualization hasn't
    shown yet."""
    while parent[x] != x:
        x = parent[x]
    return x


def union_find_demo(edges_text: str) -> Generator[dict[str, Any], None, None]:
    parsed = parse_edges(edges_text)
    node_ids = ordered_node_ids(parsed)
    parent = {nid: nid for nid in node_ids}
    rank = dict.fromkeys(node_ids, 0)
    step_index = 0

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, predict: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        nodes = [
            {
                "id": nid,
                "value": nid,
                "parent": None if parent[nid] == nid else parent[nid],
                "state": (node_states or {}).get(nid, "default"),
            }
            for nid in node_ids
        ]
        step = tree_step(
            step_index=step_index,
            kind=kind,
            nodes=nodes,
            note=note,
            counters={"sets": len({_root_of(parent, nid) for nid in node_ids})},
            predict=predict,
        )
        step_index += 1
        return step

    def find(x: str) -> Generator[dict[str, Any], None, str]:
        path: list[str] = []
        cur = x
        while True:
            is_root = parent[cur] == cur
            yield emit(
                "walk",
                f"Is {cur} its own root?",
                node_states={cur: "active"},
                predict=predict_prompt(
                    f"Is {cur} its own root, or does it have a parent above it?",
                    ["It's the root", "It has a parent"],
                    "It's the root" if is_root else "It has a parent",
                ),
            )
            if is_root:
                break
            path.append(cur)
            cur = parent[cur]
        root = cur

        to_compress = [p for p in path if parent[p] != root]
        if to_compress:
            for p in to_compress:
                parent[p] = root
            yield emit(
                "compress",
                f"Path compression: {', '.join(to_compress)} now point directly to root {root}",
                node_states={**{p: "new" for p in to_compress}, root: "target"},
            )
        return root

    def union(x: str, y: str) -> Iterator[dict[str, Any]]:
        root_x = yield from find(x)
        root_y = yield from find(y)

        if root_x == root_y:
            yield emit("same-set", f"{x} and {y} are already in the same set (root {root_x})", node_states={root_x: "target"})
            return

        winner, loser = (root_x, root_y) if rank[root_x] >= rank[root_y] else (root_y, root_x)
        yield emit(
            "compare-ranks",
            f"Comparing set sizes (rank): {root_x}={rank[root_x]} vs {root_y}={rank[root_y]}",
            node_states={root_x: "active", root_y: "active"},
            predict=predict_prompt(f"Which root will the other attach to: {root_x} or {root_y}?", [root_x, root_y], winner),
        )
        parent[loser] = winner
        if rank[winner] == rank[loser]:
            rank[winner] += 1
        yield emit("union", f"{loser}'s set now attaches to {winner}", node_states={winner: "target", loser: "new"})

    yield emit("start", f"{len(node_ids)} elements, each starts as its own set")

    for src, dst, _ in parsed:
        yield emit("phase", f"Union({src}, {dst})")
        yield from union(src, dst)

    final_sets = len({_root_of(parent, nid) for nid in node_ids})
    yield emit("done", f"Done - {final_sets} set{'s' if final_sets != 1 else ''} remain")
