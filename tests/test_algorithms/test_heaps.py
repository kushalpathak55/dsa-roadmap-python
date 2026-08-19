from app.algorithms import heaps


def _heap_property_holds(nodes):
    by_id = {n["id"]: n for n in nodes}
    for node in nodes:
        if node["parent"] is not None:
            parent = by_id[node["parent"]]
            if node["value"] < parent["value"]:
                return False
    return True


def test_heap_property_holds_once_settled():
    # Mid-sift-up/down steps are allowed to transiently violate the heap
    # property (that's the whole point of visualizing the fix-up) - only the
    # state right before the *next* insert begins (i.e. after the previous
    # element's sift-up has fully settled) and the final state need to hold it.
    steps = list(heaps.binary_heap_demo([5, 3, 8, 1, 9, 2, 7]))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    insert_indices = [i for i, s in enumerate(steps) if s["kind"] == "insert"]
    settled_steps = [steps[i - 1] for i in insert_indices if i > 0] + [steps[-1]]
    assert settled_steps  # sanity: the fixture array is non-trivial
    for step in settled_steps:
        assert _heap_property_holds(step["nodes"])


def test_root_is_the_minimum_in_the_final_heap():
    steps = list(heaps.binary_heap_demo([5, 3, 8, 1, 9]))
    final_nodes = steps[-1]["nodes"]
    root = next(n for n in final_nodes if n["parent"] is None)
    assert root["value"] == min(n["value"] for n in final_nodes)


def test_extracts_up_to_extract_count_elements():
    arr = [5, 3, 8, 1, 9, 2, 7]
    steps = list(heaps.binary_heap_demo(arr))
    final_size = len(steps[-1]["nodes"])
    assert final_size == len(arr) - min(heaps.EXTRACT_COUNT, len(arr))


def test_handles_empty_input():
    steps = list(heaps.binary_heap_demo([]))
    assert steps[-1]["kind"] == "done"
    assert steps[-1]["nodes"] == []


def test_handles_fewer_elements_than_extract_count():
    steps = list(heaps.binary_heap_demo([4, 2]))
    assert steps[-1]["nodes"] == []
