"""Binary search tree demos: insert/search/delete, and the four classic
traversals (inorder/preorder/postorder/level-order). Uses the tree-family
step schema (app/algorithms/common.py:tree_step) - nodes carry a `parent`
id so the D3 renderer can build the hierarchy directly via d3.stratify.
"""

from __future__ import annotations

import itertools
from collections import deque
from collections.abc import Generator, Iterator
from typing import Any

from app.algorithms.common import predict_prompt, tree_step


class _Node:
    __slots__ = ("id", "value", "left", "right")

    def __init__(self, id_: str, value: int):
        self.id = id_
        self.value = value
        self.left: _Node | None = None
        self.right: _Node | None = None


def _count(node: _Node | None) -> int:
    if node is None:
        return 0
    return 1 + _count(node.left) + _count(node.right)


def _snapshot(root: _Node | None, node_states: dict[str, str] | None = None) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    def visit(node: _Node | None, parent_id: str | None) -> None:
        if node is None:
            return
        nodes.append(
            {
                "id": node.id,
                "value": node.value,
                "parent": parent_id,
                "state": (node_states or {}).get(node.id, "default"),
            }
        )
        visit(node.left, node.id)
        visit(node.right, node.id)

    visit(root, None)
    return nodes


def _descent_predict(value: int, current_value: int) -> dict[str, Any]:
    """The 'which way does the search go' question shared by insert and
    search - both are the same left/right/found decision at a BST node."""
    if value == current_value:
        answer = "Found here"
    elif value < current_value:
        answer = "Go left"
    else:
        answer = "Go right"
    return predict_prompt(f"Where does {value} go from {current_value}?", ["Go left", "Go right", "Found here"], answer)


def _delete_value(node: _Node | None, value: int) -> _Node | None:
    """Standard BST delete (values are unique - duplicates are skipped on insert)."""
    if node is None:
        return None
    if value < node.value:
        node.left = _delete_value(node.left, value)
    elif value > node.value:
        node.right = _delete_value(node.right, value)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.value = successor.value
        node.right = _delete_value(node.right, successor.value)
    return node


def bst_ops_demo(arr: list[int], target: int) -> Generator[dict[str, Any], None, None]:
    root: _Node | None = None
    next_id = itertools.count()
    step_index = 0

    def emit(kind: str, note: str, node_states=None, focus=None, counters=None, predict=None):
        nonlocal step_index
        step = tree_step(
            step_index=step_index,
            kind=kind,
            nodes=_snapshot(root, node_states),
            note=note,
            focus=focus or {},
            counters=counters if counters is not None else {"nodes": _count(root)},
            predict=predict,
        )
        step_index += 1
        return step

    def insert(value: int) -> Iterator[dict[str, Any]]:
        nonlocal root
        new_node = _Node(f"n{next(next_id)}", value)
        if root is None:
            root = new_node
            yield emit("insert", f"Inserted {value} as the root", node_states={new_node.id: "new"})
            return
        current = root
        while True:
            yield emit(
                "compare",
                f"Comparing {value} with {current.value}",
                node_states={current.id: "active"},
                predict=_descent_predict(value, current.value),
            )
            if value == current.value:
                yield emit("skip", f"{value} already exists - skipping duplicate")
                return
            if value < current.value:
                if current.left is None:
                    current.left = new_node
                    yield emit("insert", f"Inserted {value} as the left child of {current.value}", node_states={new_node.id: "new"})
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = new_node
                    yield emit("insert", f"Inserted {value} as the right child of {current.value}", node_states={new_node.id: "new"})
                    return
                current = current.right

    def search(value: int) -> Generator[dict[str, Any], None, _Node | None]:
        current = root
        while current is not None:
            yield emit(
                "compare",
                f"Comparing {value} with {current.value}",
                node_states={current.id: "active"},
                focus={"target": value},
                predict=_descent_predict(value, current.value),
            )
            if value == current.value:
                yield emit("found", f"Found {value}", node_states={current.id: "target"}, focus={"target": value})
                return current
            current = current.left if value < current.value else current.right
        yield emit("not_found", f"{value} not found in the tree", focus={"target": value})
        return None

    yield emit("start", "Empty tree")

    for v in arr:
        yield from insert(v)

    found_node = yield from search(target)

    if found_node is not None:
        if found_node.left is None and found_node.right is None:
            yield emit("delete-case", f"{target} is a leaf - removing it directly", node_states={found_node.id: "target"})
        elif found_node.left is None or found_node.right is None:
            yield emit("delete-case", f"{target} has one child - replacing it with that child", node_states={found_node.id: "target"})
        else:
            successor = found_node.right
            while successor.left is not None:
                successor = successor.left
            yield emit(
                "delete-case",
                f"{target} has two children - replacing it with its in-order successor {successor.value}",
                node_states={found_node.id: "target", successor.id: "active"},
            )
        root = _delete_value(root, target)
        yield emit("delete-done", f"Deleted {target}")

    yield emit("done", "Done")


def _inorder(node: _Node | None) -> Iterator[_Node]:
    if node is None:
        return
    yield from _inorder(node.left)
    yield node
    yield from _inorder(node.right)


def _preorder(node: _Node | None) -> Iterator[_Node]:
    if node is None:
        return
    yield node
    yield from _preorder(node.left)
    yield from _preorder(node.right)


def _postorder(node: _Node | None) -> Iterator[_Node]:
    if node is None:
        return
    yield from _postorder(node.left)
    yield from _postorder(node.right)
    yield node


def _level_order(root: _Node | None) -> Iterator[_Node]:
    if root is None:
        return
    queue: deque[_Node] = deque([root])
    while queue:
        node = queue.popleft()
        yield node
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


_TRAVERSALS = [
    ("inorder", _inorder),
    ("preorder", _preorder),
    ("postorder", _postorder),
    ("level-order", _level_order),
]

# Where the root falls in each traversal's visit order - the concept each
# traversal is really teaching, phrased as a single predictable fact.
_ROOT_POSITION = {
    "inorder": "In between",
    "preorder": "First",
    "postorder": "Last",
    "level-order": "First",
}


def tree_traversal_demo(arr: list[int]) -> Generator[dict[str, Any], None, None]:
    root: _Node | None = None
    next_id = itertools.count()
    step_index = 0

    def emit(kind: str, note: str, node_states=None, focus=None, predict=None):
        nonlocal step_index
        step = tree_step(
            step_index=step_index,
            kind=kind,
            nodes=_snapshot(root, node_states),
            note=note,
            focus=focus or {},
            counters={"nodes": _count(root)},
            predict=predict,
        )
        step_index += 1
        return step

    def plain_insert(value: int) -> None:
        nonlocal root
        node = _Node(f"n{next(next_id)}", value)
        if root is None:
            root = node
            return
        current = root
        while True:
            if value == current.value:
                return
            if value < current.value:
                if current.left is None:
                    current.left = node
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = node
                    return
                current = current.right

    yield emit("start", "Empty tree")
    for v in arr:
        plain_insert(v)
    yield emit("built", "Tree built from input")

    for label, order_fn in _TRAVERSALS:
        phase_predict = (
            predict_prompt(
                f"In {label} traversal, is the root ({root.value}) visited first, last, or in between its children?",
                ["First", "Last", "In between"],
                _ROOT_POSITION[label],
            )
            if root is not None
            else None
        )
        yield emit("phase", f"Starting {label} traversal", predict=phase_predict)
        visited_ids: list[str] = []
        visited_values: list[int] = []
        for node in order_fn(root):
            visited_ids.append(node.id)
            visited_values.append(node.value)
            states = {nid: "sorted" for nid in visited_ids[:-1]}
            states[node.id] = "active"
            yield emit(
                "visit",
                f"{label}: visiting {node.value}",
                node_states=states,
                focus={"traversal": label, "order": list(visited_values)},
            )
        yield emit(
            "phase-done",
            f"{label} order: {', '.join(map(str, visited_values))}",
            node_states={nid: "sorted" for nid in visited_ids},
            focus={"traversal": label, "order": visited_values},
        )

    yield emit("done", "Done")
