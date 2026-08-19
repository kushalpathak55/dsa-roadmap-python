import pytest

from app.algorithms import graphs


def test_parse_edges_plain_and_weighted():
    assert graphs.parse_edges("A-B, B-C:4") == [("A", "B", 1), ("B", "C", 4)]


def test_parse_edges_rejects_malformed_token():
    with pytest.raises(ValueError):
        graphs.parse_edges("A--B")


def test_parse_edges_rejects_empty_input():
    with pytest.raises(ValueError):
        graphs.parse_edges("")


def test_ordered_node_ids_preserves_first_appearance():
    parsed = graphs.parse_edges("C-A, A-B")
    assert graphs.ordered_node_ids(parsed) == ["C", "A", "B"]


def test_circular_layout_places_nodes_on_a_circle_of_the_given_radius():
    pos = graphs.circular_layout(["A", "B", "C", "D"], radius=100)
    for x, y in pos.values():
        assert round((x ** 2 + y ** 2) ** 0.5, 6) == 100


def test_bfs_visit_order_and_frozen_layout():
    steps = list(graphs.bfs_demo("A-B, A-C, B-D, C-D, D-E", "A"))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    assert "A, B, C, D, E" in steps[-1]["note"]

    final_states = {n["id"]: n["state"] for n in steps[-1]["nodes"]}
    assert all(state == "sorted" for state in final_states.values())

    # layout must never change across steps - only state does
    first_positions = {n["id"]: (n["x"], n["y"]) for n in steps[0]["nodes"]}
    last_positions = {n["id"]: (n["x"], n["y"]) for n in steps[-1]["nodes"]}
    assert first_positions == last_positions


def test_bfs_rejects_unknown_start_node():
    with pytest.raises(ValueError):
        list(graphs.bfs_demo("A-B, B-C", "Z"))


def test_dfs_visits_every_node_exactly_once_starting_from_start():
    steps = list(graphs.dfs_demo("A-B, A-C, B-D, C-D, D-E", "A"))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    visit_steps = [s for s in steps if s["kind"] == "visit"]
    visited_ids = [next(n["id"] for n in s["nodes"] if n["state"] == "active") for s in visit_steps]
    assert visited_ids[0] == "A"
    assert sorted(visited_ids) == ["A", "B", "C", "D", "E"]
    assert len(visited_ids) == len(set(visited_ids))  # no repeats


def test_dijkstra_computes_correct_shortest_distances():
    steps = list(graphs.dijkstra_demo("A-B:4, A-C:1, C-B:2, B-D:5, C-D:8, D-E:3", "A"))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"
    final_dist = steps[-1]["focus"]["dist"]
    assert final_dist == {"A": 0, "B": 3, "C": 1, "D": 8, "E": 11}


def test_dijkstra_tree_edge_is_replaced_when_a_shorter_path_is_found():
    # D is first reached via C (dist 9), then improved via B (dist 8) -
    # only the B-D edge should end up marked "tree", not the stale C-D one.
    steps = list(graphs.dijkstra_demo("A-B:4, A-C:1, C-B:2, B-D:5, C-D:8, D-E:3", "A"))
    final_edges = {frozenset((e["source"], e["target"])): e["state"] for e in steps[-1]["edges"]}
    assert final_edges[frozenset(("B", "D"))] == "tree"
    assert final_edges[frozenset(("C", "D"))] == "default"


def test_dijkstra_leaves_unreachable_nodes_at_none():
    steps = list(graphs.dijkstra_demo("A-B:1, C-D:1", "A"))
    final_dist = steps[-1]["focus"]["dist"]
    assert final_dist["A"] == 0
    assert final_dist["B"] == 1
    assert final_dist["C"] is None
    assert final_dist["D"] is None


def test_topological_sort_orders_a_dag_correctly():
    steps = list(graphs.topological_sort_demo("A-B, A-C, B-D, C-D, D-E"))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    order_text = steps[-1]["note"]
    order = order_text.split(": ", 1)[1].split(", ")
    position = {node: i for i, node in enumerate(order)}
    for src, dst, _ in graphs.parse_edges("A-B, A-C, B-D, C-D, D-E"):
        assert position[src] < position[dst]


def test_topological_sort_detects_a_cycle():
    steps = list(graphs.topological_sort_demo("A-B, B-C, C-A"))
    assert steps[-1]["kind"] == "cycle"


def test_every_graph_step_has_the_common_envelope_and_edge_schema():
    steps = list(graphs.bfs_demo("A-B", "A"))
    for i, step in enumerate(steps):
        assert step["step_index"] == i
        assert "kind" in step and "note" in step and "counters" in step
        for node in step["nodes"]:
            assert set(node.keys()) == {"id", "value", "x", "y", "state"}
        for edge in step["edges"]:
            assert set(edge.keys()) == {"source", "target", "directed", "state"}
