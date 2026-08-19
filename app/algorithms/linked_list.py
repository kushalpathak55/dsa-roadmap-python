"""Singly linked list demo: build from input, traverse, insert at tail,
delete a value, then reverse - one run exercises all four operations.
Uses the list-family step schema (app/algorithms/common.py:list_step).
"""

from __future__ import annotations

import itertools
from collections.abc import Generator
from typing import Any

from app.algorithms.common import list_step, predict_prompt


def linked_list_demo(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    nodes: list[dict[str, Any]] = []
    next_id = itertools.count()
    step_index = 0

    def default_pointers() -> dict[str, str | None]:
        return {
            "head": nodes[0]["id"] if nodes else None,
            "tail": nodes[-1]["id"] if nodes else None,
        }

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, pointers=None, counters=None, predict=None):
        nonlocal step_index
        rendered = [
            {"id": n["id"], "value": n["value"], "state": (node_states or {}).get(n["id"], "default")}
            for n in nodes
        ]
        step = list_step(
            step_index=step_index,
            kind=kind,
            layout="chain",
            nodes=rendered,
            note=note,
            pointers=pointers if pointers is not None else default_pointers(),
            counters=counters if counters is not None else {"nodes": len(nodes)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty list")

    for value in arr:
        node = {"id": f"n{next(next_id)}", "value": value}
        nodes.append(node)
        yield emit("insert", f"Appended {value}", node_states={node["id"]: "new"})

    for node in nodes:
        yield emit(
            "visit",
            f"Visiting {node['value']}",
            node_states={node["id"]: "active"},
            pointers={**default_pointers(), "current": node["id"]},
        )

    new_value = (max(arr) + 1) if arr else 1
    new_node = {"id": f"n{next(next_id)}", "value": new_value}
    nodes.append(new_node)
    yield emit("insert", f"Inserted {new_value} at the tail", node_states={new_node["id"]: "new"})

    if arr:
        target_value = arr[0]
        comparisons = 0
        found_idx = None
        for i, node in enumerate(nodes):
            comparisons += 1
            is_match = node["value"] == target_value
            yield emit(
                "search",
                f"Checking {node['value']} == {target_value}?",
                node_states={node["id"]: "active"},
                pointers={**default_pointers(), "current": node["id"]},
                counters={"nodes": len(nodes), "comparisons": comparisons},
                predict=predict_prompt(f"Is {node['value']} equal to {target_value}?", ["Yes", "No"], "Yes" if is_match else "No"),
            )
            if node["value"] == target_value:
                found_idx = i
                break
        if found_idx is not None:
            target_node = nodes[found_idx]
            yield emit(
                "locate",
                f"Found {target_value} - deleting it",
                node_states={target_node["id"]: "target"},
                counters={"nodes": len(nodes), "comparisons": comparisons},
            )
            nodes.pop(found_idx)
            yield emit("delete", f"Deleted {target_value}", counters={"nodes": len(nodes), "comparisons": comparisons})

    if len(nodes) > 1:
        yield emit("reverse-start", "Reversing the list")
        nodes.reverse()
        yield emit("reverse-done", "List reversed", pointers=default_pointers())

    yield emit("done", "Done")
