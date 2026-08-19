"""Stack (LIFO) and queue (FIFO) demos: push/enqueue every input value, then
pop/dequeue about half of them. Uses the list-family step schema (common.py:list_step).
"""

from __future__ import annotations

import itertools
from collections.abc import Generator
from typing import Any

from app.algorithms.common import list_step, predict_prompt


def _next_out_predict(order: list[dict[str, Any]], structure: str) -> dict[str, Any] | None:
    """'Which value comes off next' question for a stack/queue's peek step -
    contrasts the correct end against some other value already inside so the
    LIFO/FIFO distinction is actually being tested, not just re-read off the
    screen. Returns None when every other value happens to be a tie (no
    meaningful contrast to offer)."""
    correct = order[0]["value"]
    for other in order[1:]:
        if other["value"] != correct:
            return predict_prompt(f"Which value comes off the {structure} next?", [correct, other["value"]], correct)
    return None


def stack_demo(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    stack: list[dict[str, Any]] = []
    next_id = itertools.count()
    step_index = 0

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, predict=None):
        nonlocal step_index
        rendered = [
            {"id": n["id"], "value": n["value"], "state": (node_states or {}).get(n["id"], "default")}
            for n in stack
        ]
        step = list_step(
            step_index=step_index,
            kind=kind,
            layout="stack",
            nodes=rendered,
            note=note,
            pointers={"top": stack[-1]["id"] if stack else None},
            counters={"size": len(stack)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty stack")

    for value in arr:
        node = {"id": f"n{next(next_id)}", "value": value}
        stack.append(node)
        yield emit("push", f"Pushed {value}", node_states={node["id"]: "new"})

    pop_count = min(len(arr) // 2, len(stack)) if arr else 0
    for _ in range(pop_count):
        top = stack[-1]
        yield emit(
            "peek",
            f"Top is {top['value']}",
            node_states={top["id"]: "active"},
            predict=_next_out_predict(list(reversed(stack)), "stack"),
        )
        stack.pop()
        yield emit("pop", f"Popped {top['value']}")

    yield emit("done", "Done")


def queue_demo(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    queue: list[dict[str, Any]] = []
    next_id = itertools.count()
    step_index = 0

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, predict=None):
        nonlocal step_index
        rendered = [
            {"id": n["id"], "value": n["value"], "state": (node_states or {}).get(n["id"], "default")}
            for n in queue
        ]
        step = list_step(
            step_index=step_index,
            kind=kind,
            layout="queue",
            nodes=rendered,
            note=note,
            pointers={
                "front": queue[0]["id"] if queue else None,
                "rear": queue[-1]["id"] if queue else None,
            },
            counters={"size": len(queue)},
            predict=predict,
        )
        step_index += 1
        return step

    yield emit("start", "Empty queue")

    for value in arr:
        node = {"id": f"n{next(next_id)}", "value": value}
        queue.append(node)
        yield emit("enqueue", f"Enqueued {value}", node_states={node["id"]: "new"})

    dequeue_count = min(len(arr) // 2, len(queue)) if arr else 0
    for _ in range(dequeue_count):
        front = queue[0]
        yield emit(
            "peek",
            f"Front is {front['value']}",
            node_states={front["id"]: "active"},
            predict=_next_out_predict(queue, "queue"),
        )
        queue.pop(0)
        yield emit("dequeue", f"Dequeued {front['value']}")

    yield emit("done", "Done")
