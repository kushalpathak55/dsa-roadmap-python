from app.algorithms import linked_list


def test_builds_traverses_inserts_deletes_and_reverses():
    arr = [5, 3, 8, 1]
    steps = list(linked_list.linked_list_demo(arr))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    # build [5,3,8,1] -> insert 9 at tail -> [5,3,8,1,9] -> delete first (5)
    # -> [3,8,1,9] -> reverse -> [9,1,8,3]
    final_values = [n["value"] for n in steps[-1]["nodes"]]
    assert final_values == [9, 1, 8, 3]


def test_every_step_has_common_envelope_and_list_schema():
    steps = list(linked_list.linked_list_demo([1, 2, 3]))
    for i, step in enumerate(steps):
        assert step["step_index"] == i
        assert step["layout"] == "chain"
        assert "nodes" in step and "pointers" in step
        for node in step["nodes"]:
            assert set(node.keys()) == {"id", "value", "state"}


def test_handles_empty_input():
    steps = list(linked_list.linked_list_demo([]))
    assert steps[-1]["kind"] == "done"
    assert [n["value"] for n in steps[-1]["nodes"]] == [1]


def test_node_ids_are_unique_within_a_run():
    steps = list(linked_list.linked_list_demo([4, 4, 4]))
    last_ids = [n["id"] for n in steps[-1]["nodes"]]
    assert len(last_ids) == len(set(last_ids))
