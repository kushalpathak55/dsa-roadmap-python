from app.algorithms import trees


def test_bst_deletes_leaf_target():
    steps = list(trees.bst_ops_demo([5, 3, 8, 1, 4], target=8))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    delete_case = next(s for s in steps if s["kind"] == "delete-case")
    assert "leaf" in delete_case["note"]

    final_values = sorted(n["value"] for n in steps[-1]["nodes"])
    assert final_values == [1, 3, 4, 5]


def test_bst_deletes_two_child_node_via_successor():
    steps = list(trees.bst_ops_demo([5, 3, 8, 1, 4, 7, 9], target=5))
    delete_case = next(s for s in steps if s["kind"] == "delete-case")
    assert "two children" in delete_case["note"]

    final_values = sorted(n["value"] for n in steps[-1]["nodes"])
    assert final_values == [1, 3, 4, 7, 8, 9]
    assert 5 not in final_values


def test_bst_reports_not_found_for_missing_target():
    steps = list(trees.bst_ops_demo([5, 3, 8], target=99))
    assert any(s["kind"] == "not_found" for s in steps)
    # nothing deleted - all three original values remain
    final_values = sorted(n["value"] for n in steps[-1]["nodes"])
    assert final_values == [3, 5, 8]


def test_bst_skips_duplicate_inserts():
    steps = list(trees.bst_ops_demo([5, 5, 5], target=5))
    build_inserts = [s for s in steps if s["kind"] == "insert"]
    assert len(build_inserts) == 1  # only the first 5 actually gets inserted


def test_every_tree_step_has_parent_linked_nodes():
    steps = list(trees.bst_ops_demo([5, 3, 8], target=3))
    for step in steps:
        for node in step["nodes"]:
            assert set(node.keys()) == {"id", "value", "parent", "state"}
        # exactly one root (parent None) whenever the tree is non-empty
        if step["nodes"]:
            roots = [n for n in step["nodes"] if n["parent"] is None]
            assert len(roots) == 1


def test_traversal_orders_are_correct():
    arr = [5, 3, 8, 1, 4, 7, 9]
    steps = list(trees.tree_traversal_demo(arr))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    phase_done = [s for s in steps if s["kind"] == "phase-done"]
    assert [s["focus"]["traversal"] for s in phase_done] == ["inorder", "preorder", "postorder", "level-order"]

    inorder = next(s for s in phase_done if s["focus"]["traversal"] == "inorder")
    assert inorder["focus"]["order"] == sorted(arr)  # BST in-order = sorted order

    preorder = next(s for s in phase_done if s["focus"]["traversal"] == "preorder")
    assert preorder["focus"]["order"][0] == arr[0]  # preorder visits the root first

    level_order = next(s for s in phase_done if s["focus"]["traversal"] == "level-order")
    assert level_order["focus"]["order"][0] == arr[0]  # root is also visited first breadth-first
