"""Maps algo_key -> {family, generator, request model}. The /api/run/{algo_key} route
looks up here; a coming_soon topic simply has no matching key, and the route 404s cleanly.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator, model_validator

from app.algorithms import backtracking, dp, graphs, hashing, heaps, linked_list, searching, sorting, stacks_queues, techniques, trees, trie, union_find
from app.algorithms.common import (
    MAX_ARRAY_SIZE,
    MAX_FIB_N,
    MAX_GRAPH_EDGES,
    MAX_GRAPH_NODES,
    MAX_KNAPSACK_CAPACITY,
    MAX_KNAPSACK_ITEMS,
    MAX_LIST_SIZE,
    MAX_N_QUEENS,
    MAX_STRING_LEN,
    MAX_TREE_SIZE,
    MAX_TRIE_WORD_LEN,
    MAX_TRIE_WORDS,
)


class ArrayRequest(BaseModel):
    array: list[int]

    @field_validator("array")
    @classmethod
    def validate_array(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("array must not be empty")
        if len(value) > MAX_ARRAY_SIZE:
            raise ValueError(f"array must have at most {MAX_ARRAY_SIZE} elements")
        return value


class ArraySearchRequest(ArrayRequest):
    target: int


class ArrayWindowRequest(ArrayRequest):
    k: int

    @model_validator(mode="after")
    def validate_k(self) -> "ArrayWindowRequest":
        if self.k < 1:
            raise ValueError("k must be at least 1")
        if self.k > len(self.array):
            raise ValueError("k must be at most the array length")
        return self


class ListRequest(BaseModel):
    array: list[int]

    @field_validator("array")
    @classmethod
    def validate_array(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("array must not be empty")
        if len(value) > MAX_LIST_SIZE:
            raise ValueError(f"array must have at most {MAX_LIST_SIZE} elements")
        return value


class TreeRequest(BaseModel):
    array: list[int]

    @field_validator("array")
    @classmethod
    def validate_array(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("array must not be empty")
        if len(value) > MAX_TREE_SIZE:
            raise ValueError(f"array must have at most {MAX_TREE_SIZE} elements")
        return value


class TreeSearchRequest(TreeRequest):
    target: int


class WordsRequest(BaseModel):
    words: list[str]

    @field_validator("words")
    @classmethod
    def validate_words(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("at least one word is required")
        if len(value) > MAX_TRIE_WORDS:
            raise ValueError(f"at most {MAX_TRIE_WORDS} words are allowed")
        for word in value:
            if not word:
                raise ValueError("words must not be empty")
            if not word.isalpha():
                raise ValueError("words must contain only letters")
            if len(word) > MAX_TRIE_WORD_LEN:
                raise ValueError(f"each word must be at most {MAX_TRIE_WORD_LEN} characters")
        return [word.lower() for word in value]


def _validate_edges_syntax_and_bounds(value: str) -> str:
    parsed = graphs.parse_edges(value)  # raises ValueError on malformed tokens
    node_ids = graphs.ordered_node_ids(parsed)
    if len(node_ids) > MAX_GRAPH_NODES:
        raise ValueError(f"graph must have at most {MAX_GRAPH_NODES} nodes")
    if len(parsed) > MAX_GRAPH_EDGES:
        raise ValueError(f"graph must have at most {MAX_GRAPH_EDGES} edges")
    return value


class GraphRequest(BaseModel):
    edges: str
    start: str

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, value: str) -> str:
        return _validate_edges_syntax_and_bounds(value)

    @model_validator(mode="after")
    def validate_start_in_graph(self) -> "GraphRequest":
        node_ids = graphs.ordered_node_ids(graphs.parse_edges(self.edges))
        if self.start not in node_ids:
            raise ValueError(f"start node '{self.start}' is not in the graph")
        return self


class GraphNoStartRequest(BaseModel):
    edges: str

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, value: str) -> str:
        return _validate_edges_syntax_and_bounds(value)


class FibonacciRequest(BaseModel):
    n: int

    @field_validator("n")
    @classmethod
    def validate_n(cls, value: int) -> int:
        if value < 0:
            raise ValueError("n must not be negative")
        if value > MAX_FIB_N:
            raise ValueError(f"n must be at most {MAX_FIB_N}")
        return value


class KnapsackRequest(BaseModel):
    capacity: int
    weights: list[int]
    values: list[int]

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, value: int) -> int:
        if value < 0:
            raise ValueError("capacity must not be negative")
        if value > MAX_KNAPSACK_CAPACITY:
            raise ValueError(f"capacity must be at most {MAX_KNAPSACK_CAPACITY}")
        return value

    @model_validator(mode="after")
    def validate_items(self) -> "KnapsackRequest":
        if not self.weights:
            raise ValueError("at least one item is required")
        if len(self.weights) != len(self.values):
            raise ValueError("weights and values must have the same length")
        if len(self.weights) > MAX_KNAPSACK_ITEMS:
            raise ValueError(f"at most {MAX_KNAPSACK_ITEMS} items are allowed")
        if any(w < 0 for w in self.weights) or any(v < 0 for v in self.values):
            raise ValueError("weights and values must not be negative")
        return self


class NQueensRequest(BaseModel):
    n: int

    @field_validator("n")
    @classmethod
    def validate_n(cls, value: int) -> int:
        if value < 1:
            raise ValueError("n must be at least 1")
        if value > MAX_N_QUEENS:
            raise ValueError(f"n must be at most {MAX_N_QUEENS} (step count grows very fast)")
        return value


class LCSRequest(BaseModel):
    a: str
    b: str

    @field_validator("a", "b")
    @classmethod
    def validate_string(cls, value: str) -> str:
        if not value:
            raise ValueError("string must not be empty")
        if len(value) > MAX_STRING_LEN:
            raise ValueError(f"string must have at most {MAX_STRING_LEN} characters")
        return value


def _sort_runner(generator_fn):
    def run(payload: ArrayRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array))
        return {
            "input_echo": {"array": payload.array},
            "steps": steps,
            "result": {"array": steps[-1]["array"]},
        }

    return run


def _search_runner(generator_fn):
    def run(payload: ArraySearchRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array, payload.target))
        last = steps[-1]
        return {
            "input_echo": {"array": last["array"], "target": payload.target},
            "steps": steps,
            "result": {"found": last["kind"] == "found", "index": last["indices"]["found"]},
        }

    return run


def _window_runner(generator_fn):
    def run(payload: ArrayWindowRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array, payload.k))
        last = steps[-1]
        return {
            "input_echo": {"array": payload.array, "k": payload.k},
            "steps": steps,
            "result": {"best_sum": last["counters"]["best_sum"]},
        }

    return run


def _list_runner(generator_fn):
    def run(payload: ListRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array))
        last = steps[-1]
        return {
            "input_echo": {"array": payload.array},
            "steps": steps,
            "result": {"values": [n["value"] for n in last["nodes"]]},
        }

    return run


def _hash_runner(generator_fn):
    def run(payload: ListRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array))
        last = steps[-1]
        values = [node["value"] for bucket in last["buckets"] for node in bucket["nodes"]]
        return {
            "input_echo": {"array": payload.array},
            "steps": steps,
            "result": {"bucket_count": len(last["buckets"]), "values": values},
        }

    return run


def _tree_runner(generator_fn):
    def run(payload: TreeRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array))
        last = steps[-1]
        return {
            "input_echo": {"array": payload.array},
            "steps": steps,
            "result": {"node_count": len(last["nodes"])},
        }

    return run


def _tree_search_runner(generator_fn):
    def run(payload: TreeSearchRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.array, payload.target))
        last = steps[-1]
        return {
            "input_echo": {"array": payload.array, "target": payload.target},
            "steps": steps,
            "result": {"node_count": len(last["nodes"])},
        }

    return run


def _trie_runner(generator_fn):
    def run(payload: WordsRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.words))
        last = steps[-1]
        return {
            "input_echo": {"words": payload.words},
            "steps": steps,
            "result": {"node_count": last["counters"]["nodes"]},
        }

    return run


def _graph_runner(generator_fn):
    def run(payload: GraphRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.edges, payload.start))
        last = steps[-1]
        return {
            "input_echo": {"edges": payload.edges, "start": payload.start},
            "steps": steps,
            "result": {"node_count": len(last["nodes"])},
        }

    return run


def _graph_no_start_runner(generator_fn):
    def run(payload: GraphNoStartRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.edges))
        last = steps[-1]
        return {
            "input_echo": {"edges": payload.edges},
            "steps": steps,
            "result": {"node_count": len(last["nodes"]), "kind": last["kind"]},
        }

    return run


def _union_find_runner(generator_fn):
    def run(payload: GraphNoStartRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.edges))
        last = steps[-1]
        return {
            "input_echo": {"edges": payload.edges},
            "steps": steps,
            "result": {"sets": last["counters"]["sets"]},
        }

    return run


def _fibonacci_runner(generator_fn):
    def run(payload: FibonacciRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.n))
        last = steps[-1]
        return {
            "input_echo": {"n": payload.n},
            "steps": steps,
            "result": {"value": last["grid"][0][payload.n]},
        }

    return run


def _knapsack_runner(generator_fn):
    def run(payload: KnapsackRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.capacity, payload.weights, payload.values))
        last = steps[-1]
        return {
            "input_echo": {"capacity": payload.capacity, "weights": payload.weights, "values": payload.values},
            "steps": steps,
            "result": {"best_value": last["grid"][-1][-1]},
        }

    return run


def _n_queens_runner(generator_fn):
    def run(payload: NQueensRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.n))
        last = steps[-1]
        return {
            "input_echo": {"n": payload.n},
            "steps": steps,
            "result": {"solutions": last["counters"]["solutions"]},
        }

    return run


def _lcs_runner(generator_fn):
    def run(payload: LCSRequest) -> dict[str, Any]:
        steps = list(generator_fn(payload.a, payload.b))
        last = steps[-1]
        return {
            "input_echo": {"a": payload.a, "b": payload.b},
            "steps": steps,
            "result": {"length": last["grid"][-1][-1]},
        }

    return run


ALGORITHMS: dict[str, dict[str, Any]] = {
    "bubble_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.bubble_sort)},
    "selection_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.selection_sort)},
    "insertion_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.insertion_sort)},
    "merge_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.merge_sort)},
    "quick_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.quick_sort)},
    "heap_sort": {"family": "array", "request_model": ArrayRequest, "run": _sort_runner(sorting.heap_sort)},
    "linear_search": {"family": "array", "request_model": ArraySearchRequest, "run": _search_runner(searching.linear_search)},
    "binary_search": {"family": "array", "request_model": ArraySearchRequest, "run": _search_runner(searching.binary_search)},
    "two_pointer_sum": {"family": "array", "request_model": ArraySearchRequest, "run": _search_runner(techniques.two_pointer_sum)},
    "sliding_window_max_sum": {"family": "array", "request_model": ArrayWindowRequest, "run": _window_runner(techniques.sliding_window_max_sum)},
    "linked_list_demo": {"family": "list", "request_model": ListRequest, "run": _list_runner(linked_list.linked_list_demo)},
    "stack_demo": {"family": "list", "request_model": ListRequest, "run": _list_runner(stacks_queues.stack_demo)},
    "queue_demo": {"family": "list", "request_model": ListRequest, "run": _list_runner(stacks_queues.queue_demo)},
    "hash_table_demo": {"family": "hash", "request_model": ListRequest, "run": _hash_runner(hashing.hash_table_demo)},
    "bst_ops": {"family": "tree", "request_model": TreeSearchRequest, "run": _tree_search_runner(trees.bst_ops_demo)},
    "tree_traversal_demo": {"family": "tree", "request_model": TreeRequest, "run": _tree_runner(trees.tree_traversal_demo)},
    "binary_heap_demo": {"family": "tree", "request_model": TreeRequest, "run": _tree_runner(heaps.binary_heap_demo)},
    "trie_demo": {"family": "tree", "request_model": WordsRequest, "run": _trie_runner(trie.trie_demo)},
    "union_find_demo": {"family": "tree", "request_model": GraphNoStartRequest, "run": _union_find_runner(union_find.union_find_demo)},
    "bfs_demo": {"family": "graph", "request_model": GraphRequest, "run": _graph_runner(graphs.bfs_demo)},
    "dfs_demo": {"family": "graph", "request_model": GraphRequest, "run": _graph_runner(graphs.dfs_demo)},
    "dijkstra_demo": {"family": "graph", "request_model": GraphRequest, "run": _graph_runner(graphs.dijkstra_demo)},
    "topological_sort_demo": {"family": "graph", "request_model": GraphNoStartRequest, "run": _graph_no_start_runner(graphs.topological_sort_demo)},
    "fibonacci_memo": {"family": "dp", "request_model": FibonacciRequest, "run": _fibonacci_runner(dp.fibonacci_memo_demo)},
    "knapsack": {"family": "dp", "request_model": KnapsackRequest, "run": _knapsack_runner(dp.knapsack_demo)},
    "lcs": {"family": "dp", "request_model": LCSRequest, "run": _lcs_runner(dp.lcs_demo)},
    "n_queens": {"family": "dp", "request_model": NQueensRequest, "run": _n_queens_runner(backtracking.n_queens_demo)},
}


def get_algorithm(algo_key: str) -> dict[str, Any] | None:
    return ALGORITHMS.get(algo_key)
