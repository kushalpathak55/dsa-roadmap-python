"""Binary min-heap demo: insert (with sift-up) every input value, then
extract-min (with sift-down) a few times. Presented as a tree via the
tree-family step schema - parent id is derived from the heap array's
implicit index relationship (parent of i is (i-1)//2).
"""

from __future__ import annotations

import itertools
from collections.abc import Generator, Iterator
from typing import Any

from app.algorithms.common import predict_prompt, tree_step

EXTRACT_COUNT = 3


def _snapshot(heap: list[dict[str, Any]], node_states: dict[str, str] | None = None) -> list[dict[str, Any]]:
    nodes = []
    for i, item in enumerate(heap):
        parent_id = heap[(i - 1) // 2]["id"] if i > 0 else None
        nodes.append(
            {
                "id": item["id"],
                "value": item["value"],
                "parent": parent_id,
                "state": (node_states or {}).get(item["id"], "default"),
            }
        )
    return nodes


def binary_heap_demo(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    heap: list[dict[str, Any]] = []
    next_id = itertools.count()
    step_index = 0

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, predict: dict[str, Any] | None = None):
        nonlocal step_index
        step = tree_step(
            step_index=step_index,
            kind=kind,
            nodes=_snapshot(heap, node_states),
            note=note,
            counters={"size": len(heap)},
            predict=predict,
        )
        step_index += 1
        return step

    def sift_up(i: int) -> Iterator[dict[str, Any]]:
        while i > 0:
            parent = (i - 1) // 2
            child_smaller = heap[i]["value"] < heap[parent]["value"]
            yield emit(
                "compare",
                f"Comparing {heap[i]['value']} with parent {heap[parent]['value']}",
                node_states={heap[i]["id"]: "active", heap[parent]["id"]: "active"},
                predict=predict_prompt(
                    f"Is {heap[i]['value']} smaller than its parent {heap[parent]['value']}?",
                    ["Yes", "No"],
                    "Yes" if child_smaller else "No",
                ),
            )
            if child_smaller:
                heap[i], heap[parent] = heap[parent], heap[i]
                yield emit(
                    "swap",
                    f"Swapped {heap[i]['value']} and {heap[parent]['value']} to restore heap order",
                    node_states={heap[i]["id"]: "new", heap[parent]["id"]: "new"},
                )
                i = parent
            else:
                break

    def sift_down(i: int) -> Iterator[dict[str, Any]]:
        n = len(heap)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i

            if left < n:
                left_smaller = heap[left]["value"] < heap[smallest]["value"]
                yield emit(
                    "compare",
                    f"Is {heap[left]['value']} smaller than the current smallest, {heap[smallest]['value']}?",
                    node_states={heap[left]["id"]: "active", heap[smallest]["id"]: "active"},
                    predict=predict_prompt(
                        f"Is {heap[left]['value']} smaller than {heap[smallest]['value']}?",
                        ["Yes", "No"],
                        "Yes" if left_smaller else "No",
                    ),
                )
                if left_smaller:
                    smallest = left

            if right < n:
                right_smaller = heap[right]["value"] < heap[smallest]["value"]
                yield emit(
                    "compare",
                    f"Is {heap[right]['value']} smaller than the current smallest, {heap[smallest]['value']}?",
                    node_states={heap[right]["id"]: "active", heap[smallest]["id"]: "active"},
                    predict=predict_prompt(
                        f"Is {heap[right]['value']} smaller than {heap[smallest]['value']}?",
                        ["Yes", "No"],
                        "Yes" if right_smaller else "No",
                    ),
                )
                if right_smaller:
                    smallest = right

            if smallest == i:
                break
            yield emit(
                "swap",
                f"Swapped {heap[i]['value']} and {heap[smallest]['value']} to restore heap order",
                node_states={heap[i]["id"]: "new", heap[smallest]["id"]: "new"},
            )
            heap[i], heap[smallest] = heap[smallest], heap[i]
            i = smallest

    yield emit("start", "Empty min-heap")

    for value in arr:
        node = {"id": f"n{next(next_id)}", "value": value}
        heap.append(node)
        yield emit("insert", f"Inserted {value} at the next open leaf", node_states={node["id"]: "new"})
        yield from sift_up(len(heap) - 1)

    extract_count = min(EXTRACT_COUNT, len(heap))
    for _ in range(extract_count):
        if not heap:
            break
        top = heap[0]
        yield emit("extract", f"Extracting min {top['value']} from the root", node_states={top["id"]: "target"})
        last = heap.pop()
        if heap:
            heap[0] = last
            yield emit("replace", f"Moved last leaf {last['value']} to the root", node_states={heap[0]["id"]: "active"})
            yield from sift_down(0)
        else:
            yield emit("empty", "Heap is now empty")

    yield emit("done", "Done")
