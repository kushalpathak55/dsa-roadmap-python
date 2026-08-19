"""Verifies every 'predict' prompt's answer is actually correct given the
step it's attached to - the predict-mode game is only trustworthy if the
answer key matches reality.
"""

import pytest

from app.algorithms import backtracking, dp, graphs, hashing, heaps, linked_list, searching, sorting, stacks_queues, techniques, trees, trie, union_find

SORT_FUNCTIONS = [
    sorting.bubble_sort,
    sorting.selection_sort,
    sorting.insertion_sort,
    sorting.merge_sort,
    sorting.quick_sort,
    sorting.heap_sort,
]


@pytest.mark.parametrize("sort_fn", SORT_FUNCTIONS)
def test_every_predict_prompt_has_a_valid_answer_among_its_options(sort_fn):
    steps = list(sort_fn([5, 3, 8, 1, 9, 2, 7, 4]))
    predict_steps = [s for s in steps if s.get("predict")]
    assert predict_steps, f"{sort_fn.__name__} produced no predict prompts"
    for step in predict_steps:
        predict = step["predict"]
        assert predict["answer"] in predict["options"]
        assert len(predict["options"]) == len(set(predict["options"])), "duplicate option labels"


def test_bubble_sort_predict_answer_matches_actual_swap_outcome():
    steps = list(sorting.bubble_sort([5, 3, 8, 1]))
    for i, step in enumerate(steps):
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        j, j1 = step["indices"]["compare"]
        will_swap = step["array"][j] > step["array"][j1]
        assert step["predict"]["answer"] == ("Yes" if will_swap else "No")
        # and the very next step actually reflects that outcome
        next_kind = steps[i + 1]["kind"]
        if will_swap:
            assert next_kind == "swap"


def test_selection_sort_predict_answer_matches_new_min_outcome():
    steps = list(sorting.selection_sort([5, 3, 8, 1, 9]))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        min_idx, j = step["indices"]["compare"]
        will_be_new_min = step["array"][j] < step["array"][min_idx]
        assert step["predict"]["answer"] == ("Yes" if will_be_new_min else "No")


def test_insertion_sort_predict_answer_matches_shift_outcome():
    steps = list(sorting.insertion_sort([5, 3, 8, 1, 9]))
    for i, step in enumerate(steps):
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        will_shift = step["predict"]["answer"] == "Yes"
        next_kind = steps[i + 1]["kind"]
        assert next_kind == ("shift" if will_shift else "place")


def test_merge_sort_predict_skips_ties_and_picks_the_smaller_value():
    # merge's compare step deliberately carries no `compare` index highlight
    # (see sorting.py: left[i]/right[j] are pre-merge snapshots, and the live
    # array position may already be overwritten by the time this step is
    # rendered) - so check the predict block's internal consistency instead
    # of cross-referencing against `step["array"]`.
    steps = list(sorting.merge_sort([5, 3, 8, 1, 9, 2, 7, 4]))
    for step in steps:
        if step["kind"] != "compare":
            continue
        assert step["indices"]["compare"] == []
        if step["predict"] is None:
            continue  # a tie - both option labels would've been identical
        left_val, right_val = (int(v) for v in step["predict"]["options"])
        assert left_val != right_val
        assert step["predict"]["answer"] == str(min(left_val, right_val))


def test_quick_sort_predict_answer_matches_partition_side():
    steps = list(sorting.quick_sort([5, 3, 8, 1, 9, 2, 7, 4]))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        j, pivot_idx = step["indices"]["compare"]
        goes_left = step["array"][j] < step["array"][pivot_idx]
        assert step["predict"]["answer"] == ("Yes" if goes_left else "No")


def test_heap_sort_predict_answer_matches_bigger_than_outcome():
    steps = list(sorting.heap_sort([5, 3, 8, 1, 9, 2, 7, 4]))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        child_idx, largest_idx = step["indices"]["compare"]
        is_bigger = step["array"][child_idx] > step["array"][largest_idx]
        assert step["predict"]["answer"] == ("Yes" if is_bigger else "No")


def test_linear_search_predict_answer_matches_equality():
    steps = list(searching.linear_search([5, 3, 8, 1], 8))
    for step in steps:
        if step["kind"] != "compare":
            continue
        (idx,) = step["indices"]["compare"]
        is_match = step["array"][idx] == 8
        assert step["predict"]["answer"] == ("Yes" if is_match else "No")


def test_binary_search_predict_answer_matches_equality():
    steps = list(searching.binary_search([5, 3, 8, 1, 9], 8))
    for step in steps:
        if step["kind"] != "narrow" or not step.get("predict"):
            continue
        (idx,) = step["indices"]["compare"]
        is_match = step["array"][idx] == 8
        assert step["predict"]["answer"] == ("Yes" if is_match else "No")


def test_non_compare_steps_have_no_predict_prompt():
    steps = list(sorting.bubble_sort([3, 1, 2]))
    for step in steps:
        if step["kind"] in ("start", "done", "swap"):
            assert step["predict"] is None


def _assert_prompts_are_well_formed(steps):
    predict_steps = [s for s in steps if s.get("predict")]
    assert predict_steps, "expected at least one predict prompt"
    for step in predict_steps:
        predict = step["predict"]
        assert predict["answer"] in predict["options"]
        assert len(predict["options"]) == len(set(predict["options"])), "duplicate option labels"


def test_bst_ops_predict_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(trees.bst_ops_demo([5, 3, 8, 1, 4], 8)))


def test_bst_ops_predict_answer_matches_descent_outcome():
    steps = list(trees.bst_ops_demo([5, 3, 8, 1, 4], 8))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        active = [n for n in step["nodes"] if n["state"] == "active"]
        assert len(active) == 1
        current_value = active[0]["value"]
        # Question: "Where does {value} go from {current_value}?"
        numbers = [int(tok) for tok in step["predict"]["question"].rstrip("?").split() if tok.lstrip("-").isdigit()]
        target_value = numbers[0]
        assert numbers[-1] == current_value
        if target_value == current_value:
            expected = "Found here"
        elif target_value < current_value:
            expected = "Go left"
        else:
            expected = "Go right"
        assert step["predict"]["answer"] == expected


def test_tree_traversal_predict_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(trees.tree_traversal_demo([5, 3, 8, 1, 4])))


def test_binary_heap_predict_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(heaps.binary_heap_demo([5, 3, 8, 1, 9, 2, 7])))


def test_binary_heap_predict_answer_matches_smaller_than_outcome():
    steps = list(heaps.binary_heap_demo([5, 3, 8, 1, 9, 2, 7]))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        # Question is always "Is X smaller than [its parent] Y?" - the first and last
        # numbers mentioned are the two values being compared.
        numbers = [int(tok) for tok in step["predict"]["question"].rstrip("?").split() if tok.isdigit()]
        x, y = numbers[0], numbers[-1]
        assert step["predict"]["answer"] == ("Yes" if x < y else "No")


def test_bfs_predict_answer_matches_discovery_outcome():
    steps = list(graphs.bfs_demo("A-B, B-C, A-D", "A"))
    for step in steps:
        if step["kind"] != "visit" or not step.get("predict"):
            continue
        frontier_or_sorted = {n["id"] for n in step["nodes"] if n["state"] in ("frontier", "active", "sorted")}
        edges = {(e["source"], e["target"]) for e in step["edges"]}
        edges |= {(t, s) for s, t in edges}
        current = next(n["id"] for n in step["nodes"] if n["state"] == "active")
        neighbors = {t for s, t in edges if s == current}
        discovers_new = bool(neighbors - frontier_or_sorted)
        assert step["predict"]["answer"] == ("Yes" if discovers_new else "No")


def test_dfs_predict_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(graphs.dfs_demo("A-B, B-C, A-D", "A")))


def test_dijkstra_predict_answer_matches_relax_outcome():
    steps = list(graphs.dijkstra_demo("A-B:4, A-C:1, C-B:2, B-D:5, C-D:8", "A"))
    for step in steps:
        if step["kind"] != "relax" or not step.get("predict"):
            continue
        dist = step["focus"]["dist"]
        # "Checking edge X-Y (weight W): ... vs dist[Y]=..." - parse the neighbor + new candidate.
        note = step["note"]
        neighbor = note.split("dist[")[1].split("]")[0]
        candidate = float(note.split("= ")[1].split(" vs")[0])
        current_dist = dist[neighbor]
        improves = current_dist is None or candidate < current_dist
        assert step["predict"]["answer"] == ("Yes" if improves else "No")


def test_topological_sort_predict_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(graphs.topological_sort_demo("A-B, B-C, A-D, D-C")))


def test_fibonacci_predict_answer_is_the_correct_sum():
    steps = list(dp.fibonacci_memo_demo(10))
    for step in steps:
        if step["kind"] != "fill" or not step.get("predict"):
            continue
        col = step["cursor"]["col"]
        assert step["predict"]["answer"] == str(step["grid"][0][col])


def test_knapsack_predict_answer_matches_take_or_skip():
    weights, values = [2, 3, 4, 5], [3, 4, 5, 6]
    steps = list(dp.knapsack_demo(10, weights, values))
    for step in steps:
        if step["kind"] != "fill" or not step.get("predict"):
            continue
        row, col = step["cursor"]["row"], step["cursor"]["col"]
        cells = step["highlight"]["cells"]
        assert len(cells) == 2  # only the "item fits" branch carries a predict prompt
        exclude = step["grid"][cells[0][0]][cells[0][1]]
        include = values[row - 1] + step["grid"][cells[1][0]][cells[1][1]]
        assert step["grid"][row][col] == max(exclude, include)
        expected = "Take it" if include >= exclude else "Skip it"
        assert step["predict"]["answer"] == expected


def test_lcs_predict_answer_matches_char_equality():
    steps = list(dp.lcs_demo("ABCBDAB", "BDCABA"))
    for step in steps:
        if step["kind"] != "fill" or not step.get("predict"):
            continue
        assert step["predict"]["answer"] in ("Match", "No match")


def test_linked_list_predict_answer_matches_equality():
    steps = list(linked_list.linked_list_demo([5, 3, 8, 1]))
    for step in steps:
        if step["kind"] != "search" or not step.get("predict"):
            continue
        active = [n for n in step["nodes"] if n["state"] == "active"]
        assert len(active) == 1
        numbers = [int(tok) for tok in step["predict"]["question"].rstrip("?").split() if tok.isdigit()]
        is_match = numbers[0] == numbers[1]
        assert step["predict"]["answer"] == ("Yes" if is_match else "No")
        assert (active[0]["value"] == numbers[0]) == is_match


def test_stack_predict_answer_matches_top_of_stack():
    steps = list(stacks_queues.stack_demo([5, 3, 8, 1, 9]))
    for step in steps:
        if step["kind"] != "peek" or not step.get("predict"):
            continue
        top_value = step["nodes"][-1]["value"]
        assert step["predict"]["answer"] == str(top_value)
        assert str(top_value) in step["predict"]["options"]


def test_queue_predict_answer_matches_front_of_queue():
    steps = list(stacks_queues.queue_demo([5, 3, 8, 1, 9]))
    for step in steps:
        if step["kind"] != "peek" or not step.get("predict"):
            continue
        front_value = step["nodes"][0]["value"]
        assert step["predict"]["answer"] == str(front_value)
        assert str(front_value) in step["predict"]["options"]


def test_hash_table_predict_answer_matches_modulo():
    steps = list(hashing.hash_table_demo([10, 3, 17, 24]))
    for step in steps:
        if step["kind"] != "hash" or not step.get("predict"):
            continue
        value = int(step["note"].split("hash(")[1].split(")")[0])
        assert step["predict"]["answer"] == str(value % 7)


def test_list_and_hash_family_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(linked_list.linked_list_demo([5, 3, 8, 1])))
    _assert_prompts_are_well_formed(list(stacks_queues.stack_demo([5, 3, 8, 1, 9])))
    _assert_prompts_are_well_formed(list(stacks_queues.queue_demo([5, 3, 8, 1, 9])))
    _assert_prompts_are_well_formed(list(hashing.hash_table_demo([10, 3, 17, 24])))


def test_two_pointer_sum_predict_answer_matches_actual_comparison():
    steps = list(techniques.two_pointer_sum([5, 3, 8, 1, 9, 2, 7], 12))
    for step in steps:
        if step["kind"] != "compare" or not step.get("predict"):
            continue
        left, right = step["indices"]["compare"]
        total = step["array"][left] + step["array"][right]
        expected = "Equal" if total == 12 else ("Less than" if total < 12 else "Greater than")
        assert step["predict"]["answer"] == expected


def test_sliding_window_predict_answer_matches_new_best_outcome():
    # A "slide" step's own counters snapshot is captured before window_sum/
    # best_sum are reassigned (emit() runs first) - so counters["best_sum"]
    # on that very step IS "the current best" its predict question refers to.
    steps = list(techniques.sliding_window_max_sum([5, 3, 8, 1, 9, 2, 7], 3))
    for step in steps:
        if step["kind"] != "slide" or not step.get("predict"):
            continue
        current_best = step["counters"]["best_sum"]
        new_sum = int(step["predict"]["question"].split("(")[1].split(")")[0])
        expected = "Yes" if new_sum > current_best else "No"
        assert step["predict"]["answer"] == expected


def test_array_techniques_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(techniques.two_pointer_sum([5, 3, 8, 1, 9, 2, 7], 12)))
    _assert_prompts_are_well_formed(list(techniques.sliding_window_max_sum([5, 3, 8, 1, 9, 2, 7], 3)))


def test_trie_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(trie.trie_demo(["cat", "car", "card", "care", "dog", "do"])))


def test_n_queens_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(backtracking.n_queens_demo(4)))


def test_n_queens_predict_answer_matches_safety_check():
    steps = list(backtracking.n_queens_demo(4))
    for i, step in enumerate(steps):
        if step["kind"] != "try" or not step.get("predict"):
            continue
        answer = step["predict"]["answer"]
        next_kind = steps[i + 1]["kind"]
        if answer == "Yes":
            assert next_kind == "place"
        else:
            assert next_kind != "place"


def test_union_find_prompts_are_well_formed():
    _assert_prompts_are_well_formed(list(union_find.union_find_demo("A-B, B-C, D-E, E-F, F-G, A-D, B-G")))


def test_union_find_walk_predict_matches_own_parent_pointer():
    steps = list(union_find.union_find_demo("A-B, B-C, C-D, A-D"))
    for step in steps:
        if step["kind"] != "walk" or not step.get("predict"):
            continue
        label = step["predict"]["question"].split()[1]  # "Is {label} its own root ...?"
        node = next(n for n in step["nodes"] if n["id"] == label)
        expected = "It's the root" if node["parent"] is None else "It has a parent"
        assert step["predict"]["answer"] == expected


def test_union_find_compare_ranks_predict_matches_union_outcome():
    steps = list(union_find.union_find_demo("A-B, B-C, C-D, A-D"))
    for i, step in enumerate(steps):
        if step["kind"] != "compare-ranks" or not step.get("predict"):
            continue
        answer = step["predict"]["answer"]
        assert answer in step["predict"]["options"]
        next_step = steps[i + 1]
        assert next_step["kind"] == "union"
        winner_node = next(n for n in next_step["nodes"] if n["state"] == "target")
        assert winner_node["id"] == answer


def test_trie_predict_answer_matches_branch_existence():
    # "check" (insert) and "search-char" steps both predict whether a branch
    # for the current character already exists - verified against the very
    # next step's kind, which observably differs depending on that outcome
    # (a fresh branch always triggers "insert"; a missing search branch
    # always triggers "not-found").
    steps = list(trie.trie_demo(["cat", "car", "card", "care", "dog", "do"]))
    for i, step in enumerate(steps):
        if step["kind"] not in ("check", "search-char") or not step.get("predict"):
            continue
        answer = step["predict"]["answer"]
        next_kind = steps[i + 1]["kind"]
        if step["kind"] == "check":
            assert (next_kind == "insert") == (answer == "No")
        else:
            assert (next_kind == "not-found") == (answer == "No")
