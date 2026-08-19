"""Hash table with separate chaining. Own step schema (not the list-family one)
since a hash table is an array of chains, not a single chain/stack/queue - but
the renderer still reuses the DOM-box building blocks from list_boxes.js.
"""

from __future__ import annotations

import itertools
from collections.abc import Generator
from typing import Any

from app.algorithms.common import predict_prompt

TABLE_SIZE = 7


def hash_table_demo(arr: list[int], table_size: int = TABLE_SIZE) -> Generator[dict[str, Any], None, None]:
    arr = list(arr)
    buckets: list[list[dict[str, Any]]] = [[] for _ in range(table_size)]
    next_id = itertools.count()
    step_index = 0

    def emit(
        kind: str,
        note: str,
        active_bucket: int | None = None,
        node_states: dict[str, str] | None = None,
        predict: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal step_index
        rendered_buckets = [
            {
                "index": i,
                "nodes": [
                    {"id": n["id"], "value": n["value"], "state": (node_states or {}).get(n["id"], "default")}
                    for n in bucket
                ],
            }
            for i, bucket in enumerate(buckets)
        ]
        step = {
            "step_index": step_index,
            "kind": kind,
            "buckets": rendered_buckets,
            "active_bucket": active_bucket,
            "note": note,
            "counters": {"size": sum(len(b) for b in buckets), "buckets": table_size},
            "predict": predict,
        }
        step_index += 1
        return step

    def bucket_predict(value: int, idx: int) -> dict[str, Any] | None:
        distractors = [b for b in range(table_size) if b != idx][:2]
        if not distractors:
            return None
        options = [idx, *distractors]
        return predict_prompt(f"Which bucket will {value} land in? (hash = value % {table_size})", options, idx)

    yield emit("start", f"Empty hash table with {table_size} buckets")

    for value in arr:
        idx = value % table_size
        yield emit(
            "hash",
            f"hash({value}) = {value} % {table_size} = {idx}",
            active_bucket=idx,
            predict=bucket_predict(value, idx),
        )

        if buckets[idx]:
            yield emit(
                "collision",
                f"Bucket {idx} already has {len(buckets[idx])} item(s) - chaining onto it",
                active_bucket=idx,
            )

        node = {"id": f"n{next(next_id)}", "value": value}
        buckets[idx].append(node)
        yield emit(
            "insert",
            f"Inserted {value} into bucket {idx}",
            active_bucket=idx,
            node_states={node["id"]: "new"},
        )

    yield emit("done", "Done")
