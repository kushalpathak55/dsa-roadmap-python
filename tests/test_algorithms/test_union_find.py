import random

import pytest

from app.algorithms.union_find import union_find_demo


def _brute_force_set_count(edges: list[tuple[str, str]]) -> int:
    nodes = sorted({a for a, _ in edges} | {b for _, b in edges})
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return len({find(n) for n in nodes})


@pytest.mark.parametrize("seed", range(50))
def test_union_find_set_count_matches_brute_force(seed):
    rng = random.Random(seed)
    letters = "ABCDEFGH"
    n_edges = rng.randint(1, 12)
    edges = [(rng.choice(letters), rng.choice(letters)) for _ in range(n_edges)]
    edges_text = ", ".join(f"{a}-{b}" for a, b in edges)

    steps = list(union_find_demo(edges_text))
    assert steps[-1]["counters"]["sets"] == _brute_force_set_count(edges)


def test_union_find_envelope():
    steps = list(union_find_demo("A-B, B-C, D-E, E-F, F-G, A-D, B-G"))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert steps[0]["counters"]["sets"] == 7  # 7 distinct letters, all singletons
    assert steps[-1]["counters"]["sets"] == 1  # everything ends up connected


def test_union_find_handles_repeated_union_as_same_set():
    steps = list(union_find_demo("A-B, A-B"))
    kinds = [s["kind"] for s in steps]
    assert "same-set" in kinds


def test_union_find_path_compression_actually_flattens_parent_pointers():
    # A chain A-B, B-C, C-D forces union-by-rank to build depth before the
    # final find - after it, every visited node should point directly at the
    # tree's root (not just at its old immediate parent).
    steps = list(union_find_demo("A-B, B-C, C-D"))
    compress_steps = [s for s in steps if s["kind"] == "compress"]
    for step in compress_steps:
        by_id = {n["id"]: n for n in step["nodes"]}
        root_id = next(n["id"] for n in step["nodes"] if n["state"] == "target")
        for node in step["nodes"]:
            if node["state"] == "new":
                assert node["parent"] == root_id


def test_union_find_forest_before_any_unions_has_multiple_roots():
    steps = list(union_find_demo("A-B, C-D"))
    start = steps[0]
    roots = [n for n in start["nodes"] if n["parent"] is None]
    assert len(roots) == 4  # A, B, C, D all start as their own root
