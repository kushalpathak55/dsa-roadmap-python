"""Graph algorithms: BFS, DFS, Dijkstra, and topological sort (Kahn's algorithm).

Edge input syntax (shared across all four): comma-separated `A-B` or `A-B:weight`
tokens, e.g. "A-B, B-C:4, A-C". For BFS/DFS/Dijkstra edges are treated as
undirected; for topological sort, reading order is the direction (A-B means
"A before B"), matching a DAG's natural left-to-right reading.

Layout is computed once (circular_layout) and frozen into every step - see
graph_step's docstring in common.py for why that matters.
"""

from __future__ import annotations

import math
import re
from collections import deque
from collections.abc import Generator
from typing import Any

from app.algorithms.common import graph_step, predict_prompt

_EDGE_RE = re.compile(r"^([A-Za-z0-9]+)-([A-Za-z0-9]+)(?::(\d+))?$")


def parse_edges(text: str) -> list[tuple[str, str, int]]:
    edges: list[tuple[str, str, int]] = []
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        match = _EDGE_RE.match(token)
        if not match:
            raise ValueError(f"Invalid edge '{token}' - expected 'A-B' or 'A-B:weight'")
        src, dst, weight = match.groups()
        edges.append((src, dst, int(weight) if weight else 1))
    if not edges:
        raise ValueError("At least one edge is required")
    return edges


def ordered_node_ids(edges: list[tuple[str, str, int]]) -> list[str]:
    seen: list[str] = []
    for src, dst, _ in edges:
        if src not in seen:
            seen.append(src)
        if dst not in seen:
            seen.append(dst)
    return seen


def circular_layout(node_ids: list[str], radius: float = 150.0) -> dict[str, tuple[float, float]]:
    n = len(node_ids)
    positions = {}
    for i, node_id in enumerate(node_ids):
        angle = (2 * math.pi * i / n) - (math.pi / 2)
        positions[node_id] = (radius * math.cos(angle), radius * math.sin(angle))
    return positions


def _dedupe_undirected(edges: list[tuple[str, str, int]]) -> list[tuple[str, str]]:
    seen: set[frozenset[str]] = set()
    result = []
    for src, dst, _ in edges:
        key = frozenset((src, dst))
        if key in seen:
            continue
        seen.add(key)
        result.append((src, dst))
    return result


def _dedupe_directed(edges: list[tuple[str, str, int]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    result = []
    for src, dst, _ in edges:
        if (src, dst) in seen:
            continue
        seen.add((src, dst))
        result.append((src, dst))
    return result


def bfs_demo(edges_text: str, start: str) -> Generator[dict[str, Any], None, None]:
    parsed = parse_edges(edges_text)
    node_ids = ordered_node_ids(parsed)
    if start not in node_ids:
        raise ValueError(f"Start node '{start}' is not in the graph")
    pos = circular_layout(node_ids)
    adjacency: dict[str, list[str]] = {n: [] for n in node_ids}
    for src, dst, _ in parsed:
        if dst not in adjacency[src]:
            adjacency[src].append(dst)
        if src not in adjacency[dst]:
            adjacency[dst].append(src)
    canonical_edges = _dedupe_undirected(parsed)

    node_state: dict[str, str] = {}
    edge_state: dict[tuple[str, str], str] = {}
    step_index = 0

    def emit(kind: str, note: str, counters: dict[str, int] | None = None, predict: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        nodes_out = [
            {"id": n, "value": n, "x": pos[n][0], "y": pos[n][1], "state": node_state.get(n, "default")}
            for n in node_ids
        ]
        edges_out = [
            {"source": s, "target": t, "directed": False, "state": edge_state.get((s, t)) or edge_state.get((t, s)) or "default"}
            for s, t in canonical_edges
        ]
        step = graph_step(
            step_index=step_index,
            kind=kind,
            nodes=nodes_out,
            edges=edges_out,
            note=note,
            counters=counters if counters is not None else {"visited": sum(1 for v in node_state.values() if v == "sorted")},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", f"Starting BFS from {start}")

    queue: deque[str] = deque([start])
    enqueued = {start}
    node_state[start] = "frontier"
    yield emit("enqueue", f"Enqueued {start}. Queue: [{', '.join(queue)}]")

    visited_order: list[str] = []
    while queue:
        current = queue.popleft()
        node_state[current] = "active"
        visited_order.append(current)
        discovers_new = any(neighbor not in enqueued for neighbor in adjacency[current])
        yield emit(
            "visit",
            f"Visiting {current}. Queue: [{', '.join(queue)}]",
            predict=predict_prompt(
                f"Will visiting {current} discover any brand-new (not-yet-seen) neighbor?",
                ["Yes", "No"],
                "Yes" if discovers_new else "No",
            ),
        )
        for neighbor in adjacency[current]:
            if neighbor not in enqueued:
                enqueued.add(neighbor)
                node_state[neighbor] = "frontier"
                edge_state[(current, neighbor)] = "tree"
                queue.append(neighbor)
                yield emit("enqueue", f"Enqueued {neighbor} via {current}. Queue: [{', '.join(queue)}]")
        node_state[current] = "sorted"

    yield emit("done", f"BFS complete. Visit order: {', '.join(visited_order)}", counters={"visited": len(visited_order)})


def dfs_demo(edges_text: str, start: str) -> Generator[dict[str, Any], None, None]:
    parsed = parse_edges(edges_text)
    node_ids = ordered_node_ids(parsed)
    if start not in node_ids:
        raise ValueError(f"Start node '{start}' is not in the graph")
    pos = circular_layout(node_ids)
    adjacency: dict[str, list[str]] = {n: [] for n in node_ids}
    for src, dst, _ in parsed:
        if dst not in adjacency[src]:
            adjacency[src].append(dst)
        if src not in adjacency[dst]:
            adjacency[dst].append(src)
    canonical_edges = _dedupe_undirected(parsed)

    node_state: dict[str, str] = {}
    edge_state: dict[tuple[str, str], str] = {}
    step_index = 0

    def emit(kind: str, note: str, counters: dict[str, int] | None = None, predict: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        nodes_out = [
            {"id": n, "value": n, "x": pos[n][0], "y": pos[n][1], "state": node_state.get(n, "default")}
            for n in node_ids
        ]
        edges_out = [
            {"source": s, "target": t, "directed": False, "state": edge_state.get((s, t)) or edge_state.get((t, s)) or "default"}
            for s, t in canonical_edges
        ]
        step = graph_step(
            step_index=step_index,
            kind=kind,
            nodes=nodes_out,
            edges=edges_out,
            note=note,
            counters=counters if counters is not None else {"visited": sum(1 for v in node_state.values() if v == "sorted")},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", f"Starting DFS from {start}")

    stack: list[tuple[str, str | None]] = [(start, None)]
    visited: set[str] = set()
    order: list[str] = []
    while stack:
        current, via = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)
        if via is not None:
            edge_state[(via, current)] = "tree"
        node_state[current] = "active"
        stack_labels = [n for n, _ in stack]
        pushes_new = any(neighbor not in visited for neighbor in adjacency[current])
        yield emit(
            "visit",
            f"Visiting {current}. Stack: [{', '.join(stack_labels)}]",
            predict=predict_prompt(
                f"Will visiting {current} push any brand-new (not-yet-visited) neighbor onto the stack?",
                ["Yes", "No"],
                "Yes" if pushes_new else "No",
            ),
        )
        for neighbor in reversed(adjacency[current]):
            if neighbor not in visited:
                stack.append((neighbor, current))
                stack_labels = [n for n, _ in stack]
                yield emit("push", f"Pushed {neighbor} onto the stack. Stack: [{', '.join(stack_labels)}]")
        node_state[current] = "sorted"

    yield emit("done", f"DFS complete. Visit order: {', '.join(order)}", counters={"visited": len(order)})


def dijkstra_demo(edges_text: str, start: str) -> Generator[dict[str, Any], None, None]:
    parsed = parse_edges(edges_text)
    node_ids = ordered_node_ids(parsed)
    if start not in node_ids:
        raise ValueError(f"Start node '{start}' is not in the graph")
    pos = circular_layout(node_ids)
    adjacency: dict[str, list[tuple[str, int]]] = {n: [] for n in node_ids}
    for src, dst, weight in parsed:
        adjacency[src].append((dst, weight))
        adjacency[dst].append((src, weight))
    canonical_edges = _dedupe_undirected(parsed)

    dist: dict[str, float] = {n: math.inf for n in node_ids}
    dist[start] = 0
    node_state: dict[str, str] = {}
    # Keyed by the *improved* node, not a flat edge set - a later relaxation
    # can replace an earlier tree edge into the same node, and the earlier
    # one must stop rendering as "tree" once that happens (otherwise a stale
    # now-suboptimal edge stays highlighted forever).
    incoming_tree_edge: dict[str, tuple[str, str]] = {}
    step_index = 0

    def is_tree_edge(s: str, t: str) -> bool:
        for node in (s, t):
            pair = incoming_tree_edge.get(node)
            if pair and set(pair) == {s, t}:
                return True
        return False

    def emit(kind: str, note: str, predict: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        nodes_out = [
            {"id": n, "value": n, "x": pos[n][0], "y": pos[n][1], "state": node_state.get(n, "default")}
            for n in node_ids
        ]
        edges_out = [
            {"source": s, "target": t, "directed": False, "state": "tree" if is_tree_edge(s, t) else "default"}
            for s, t in canonical_edges
        ]
        step = graph_step(
            step_index=step_index,
            kind=kind,
            nodes=nodes_out,
            edges=edges_out,
            note=note,
            focus={"dist": {n: (None if dist[n] == math.inf else dist[n]) for n in node_ids}},
            counters={"visited": sum(1 for v in node_state.values() if v == "sorted")},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", f"Starting Dijkstra from {start}. dist[{start}] = 0")

    visited: set[str] = set()
    while len(visited) < len(node_ids):
        candidates = [n for n in node_ids if n not in visited and dist[n] < math.inf]
        if not candidates:
            break
        current = min(candidates, key=lambda n: dist[n])
        node_state[current] = "active"
        yield emit("select", f"Selecting closest unvisited node: {current} (dist={dist[current]})")
        visited.add(current)
        for neighbor, weight in adjacency[current]:
            if neighbor in visited:
                continue
            candidate = dist[current] + weight
            current_label = "∞" if dist[neighbor] == math.inf else dist[neighbor]
            improves = candidate < dist[neighbor]
            yield emit(
                "relax",
                f"Checking edge {current}-{neighbor} (weight {weight}): {dist[current]} + {weight} = {candidate} vs dist[{neighbor}]={current_label}",
                predict=predict_prompt(
                    f"Does going through {current} improve dist[{neighbor}] (currently {current_label})?",
                    ["Yes", "No"],
                    "Yes" if improves else "No",
                ),
            )
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                incoming_tree_edge[neighbor] = (current, neighbor)
                yield emit("update", f"Updated dist[{neighbor}] = {candidate} via {current}")
        node_state[current] = "sorted"

    summary = ", ".join(f"{n}={'∞' if dist[n] == math.inf else dist[n]}" for n in node_ids)
    yield emit("done", f"Dijkstra complete. Distances: {summary}")


def topological_sort_demo(edges_text: str) -> Generator[dict[str, Any], None, None]:
    parsed = parse_edges(edges_text)
    node_ids = ordered_node_ids(parsed)
    pos = circular_layout(node_ids)
    adjacency: dict[str, list[str]] = {n: [] for n in node_ids}
    in_degree: dict[str, int] = dict.fromkeys(node_ids, 0)
    for src, dst, _ in parsed:
        adjacency[src].append(dst)
        in_degree[dst] += 1
    canonical_edges = _dedupe_directed(parsed)

    node_state: dict[str, str] = {}
    edge_state: dict[tuple[str, str], str] = {}
    step_index = 0

    def emit(kind: str, note: str, predict: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        nodes_out = [
            {"id": n, "value": n, "x": pos[n][0], "y": pos[n][1], "state": node_state.get(n, "default")}
            for n in node_ids
        ]
        edges_out = [
            {"source": s, "target": t, "directed": True, "state": edge_state.get((s, t), "default")}
            for s, t in canonical_edges
        ]
        step = graph_step(
            step_index=step_index,
            kind=kind,
            nodes=nodes_out,
            edges=edges_out,
            note=note,
            focus={"in_degree": dict(in_degree)},
            counters={"ordered": sum(1 for v in node_state.values() if v == "sorted")},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Computing in-degrees: " + ", ".join(f"{n}={in_degree[n]}" for n in node_ids))

    queue: deque[str] = deque(n for n in node_ids if in_degree[n] == 0)
    for n in queue:
        node_state[n] = "frontier"
    yield emit("enqueue", f"Nodes with in-degree 0: [{', '.join(queue)}]")

    order: list[str] = []
    while queue:
        current = queue.popleft()
        node_state[current] = "active"
        order.append(current)
        makes_ready = any(in_degree[neighbor] == 1 for neighbor in adjacency[current])
        yield emit(
            "visit",
            f"Removing {current} from the graph. Order so far: [{', '.join(order)}]",
            predict=predict_prompt(
                f"Will removing {current} make any neighbor's in-degree reach 0 (ready to enqueue)?",
                ["Yes", "No"],
                "Yes" if makes_ready else "No",
            ),
        )
        for neighbor in adjacency[current]:
            in_degree[neighbor] -= 1
            edge_state[(current, neighbor)] = "tree"
            yield emit("decrement", f"Decremented in-degree of {neighbor} to {in_degree[neighbor]}")
            if in_degree[neighbor] == 0:
                node_state[neighbor] = "frontier"
                queue.append(neighbor)
                yield emit("enqueue", f"{neighbor} now has in-degree 0 - enqueued. Queue: [{', '.join(queue)}]")
        node_state[current] = "sorted"

    if len(order) < len(node_ids):
        remaining = [n for n in node_ids if n not in order]
        for n in remaining:
            node_state[n] = "target"
        yield emit("cycle", f"Cycle detected - {', '.join(remaining)} could not be ordered")
    else:
        yield emit("done", f"Topological order: {', '.join(order)}")
