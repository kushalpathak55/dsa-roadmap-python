"""Trie (prefix tree) demo: insert a batch of words character-by-character
(sharing existing branches where prefixes overlap), then search a few words
to show the trie's key distinction other structures don't have - a string
can exist only as a PREFIX of something inserted, without being a complete
word itself. Uses the tree-family step schema (parent-pointer nodes), same
renderer as BST/heap - a node's value is just a character instead of a number.
"""

from __future__ import annotations

import itertools
from collections.abc import Generator, Iterator
from typing import Any

from app.algorithms.common import predict_prompt, tree_step

ROOT_LABEL = "•"


class _TrieNode:
    __slots__ = ("id", "char", "children", "is_word")

    def __init__(self, id_: str, char: str):
        self.id = id_
        self.char = char
        self.children: dict[str, "_TrieNode"] = {}
        self.is_word = False


def _snapshot(root: _TrieNode, node_states: dict[str, str] | None = None) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    def visit(node: _TrieNode, parent_id: str | None) -> None:
        state = (node_states or {}).get(node.id)
        if state is None:
            # A word-end node stays visually marked ("target") even outside
            # the step that just touched it - otherwise there'd be no way to
            # tell a complete word apart from a node that's merely a shared
            # prefix once the demo has moved on to the next word.
            state = "target" if node.is_word else "default"
        nodes.append({"id": node.id, "value": node.char, "parent": parent_id, "state": state})
        for child in node.children.values():
            visit(child, node.id)

    visit(root, None)
    return nodes


def _count(node: _TrieNode) -> int:
    return 1 + sum(_count(c) for c in node.children.values())


def trie_demo(words: list[str]) -> Generator[dict[str, Any], None, None]:
    next_id = itertools.count()
    root = _TrieNode(f"n{next(next_id)}", ROOT_LABEL)
    step_index = 0

    def emit(kind: str, note: str, node_states: dict[str, str] | None = None, predict=None) -> dict[str, Any]:
        nonlocal step_index
        step = tree_step(
            step_index=step_index,
            kind=kind,
            nodes=_snapshot(root, node_states),
            note=note,
            counters={"nodes": _count(root)},
            predict=predict,
        )
        step_index += 1
        return step

    def insert(word: str) -> Iterator[dict[str, Any]]:
        current = root
        prefix = ""
        for ch in word:
            branch_exists = ch in current.children
            yield emit(
                "check",
                f"Looking for '{ch}' after \"{prefix}\"",
                node_states={current.children[ch].id: "active"} if branch_exists else {},
                predict=predict_prompt(f"Does a branch for '{ch}' already exist here?", ["Yes", "No"], "Yes" if branch_exists else "No"),
            )
            if not branch_exists:
                new_node = _TrieNode(f"n{next(next_id)}", ch)
                current.children[ch] = new_node
                yield emit("insert", f"No branch yet - creating a new node for '{ch}'", node_states={new_node.id: "new"})
            current = current.children[ch]
            prefix += ch
        if not current.is_word:
            current.is_word = True
            yield emit("word-complete", f"\"{word}\" is now a complete word in the trie", node_states={current.id: "target"})
        else:
            yield emit("already-word", f"\"{word}\" was already in the trie", node_states={current.id: "target"})

    def search(word: str) -> Iterator[dict[str, Any]]:
        current = root
        path_ids: list[str] = []
        for i, ch in enumerate(word):
            prefix = word[: i + 1]
            branch_exists = ch in current.children
            trail_states = {pid: "sorted" for pid in path_ids}
            if branch_exists:
                trail_states[current.children[ch].id] = "active"
            yield emit(
                "search-char",
                f"Looking for '{ch}' (building \"{prefix}\")",
                node_states=trail_states,
                predict=predict_prompt(f"Does the trie have a branch for '{ch}' here?", ["Yes", "No"], "Yes" if branch_exists else "No"),
            )
            if not branch_exists:
                yield emit("not-found", f"No branch for '{ch}' - \"{word}\" is not in the trie", node_states={pid: "sorted" for pid in path_ids})
                return
            current = current.children[ch]
            path_ids.append(current.id)

        trail_states = {pid: "sorted" for pid in path_ids[:-1]}
        if current.is_word:
            trail_states[current.id] = "target"
            yield emit("found", f"\"{word}\" is a complete word in the trie", node_states=trail_states)
        else:
            trail_states[current.id] = "active"
            yield emit("prefix-only", f"\"{word}\" exists only as a PREFIX here, not a complete word", node_states=trail_states)

    yield emit("start", "Empty trie")

    for word in words:
        yield from insert(word)

    yield emit("phase", f"Searching for \"{words[0]}\" (was inserted - should be a complete word)")
    yield from search(words[0])

    if len(words[0]) > 1:
        stub = words[0][:-1]
        yield emit("phase", f"Searching for \"{stub}\" (a prefix of \"{words[0]}\" - is it a complete word too?)")
        yield from search(stub)

    miss = words[0][0] + "zzz"
    yield emit("phase", f"Searching for \"{miss}\" (not expected to be in the trie)")
    yield from search(miss)

    yield emit("done", "Done")
