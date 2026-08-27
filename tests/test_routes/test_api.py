import html

import pytest
import yaml
from fastapi.testclient import TestClient

from app.algorithms.registry import ALGORITHMS
from app.content.loader import CONTENT_DIR, TOPICS_YAML, load_roadmap
from app.main import app

client = TestClient(app)


def all_slugs():
    _, by_slug = load_roadmap()
    return list(by_slug.keys())


@pytest.mark.parametrize("slug", all_slugs())
def test_every_topic_page_returns_200(slug):
    response = client.get(f"/topic/{slug}")
    assert response.status_code == 200


def test_home_page_lists_all_categories():
    response = client.get("/")
    assert response.status_code == 200
    categories, _ = load_roadmap()
    for category in categories:
        assert html.escape(category.name) in response.text


def test_unknown_topic_404s():
    response = client.get("/topic/does-not-exist")
    assert response.status_code == 404


def test_built_topic_renders_run_panel():
    response = client.get("/topic/bubble-sort")
    assert response.status_code == 200
    assert 'id="btn-run"' in response.text


def test_content_only_topic_has_no_run_panel_or_coming_soon_banner():
    # Big-O is a concept, not a procedure - it has finished content but no
    # algorithm to run, so it should show neither a run panel nor the
    # "coming soon" placeholder.
    response = client.get("/topic/big-o")
    assert response.status_code == 200
    assert 'id="btn-run"' not in response.text
    assert "coming soon" not in response.text.lower()
    assert "Big-O notation describes" in response.text


def test_no_topic_is_left_as_a_coming_soon_placeholder():
    # The roadmap is fully built out - every topic is either "built" (has a
    # live visualizer) or "content_only" (written, no algorithm to run).
    _, by_slug = load_roadmap()
    coming_soon = [t.slug for t in by_slug.values() if t.status == "coming_soon"]
    assert coming_soon == []


def test_every_topic_has_guided_mode_reasoning():
    # Guided Mode's "why this topic, why now" copy comes from topics.yaml's
    # `why` field - a topic silently missing it would show a blank reason
    # instead of failing loudly, so this guards against that at load time.
    _, by_slug = load_roadmap()
    missing = [t.slug for t in by_slug.values() if not t.why.strip()]
    assert missing == []


def test_home_page_and_nav_show_no_soon_badges():
    # Regression: the nav/home "soon" badge must key off is_coming_soon, not
    # `not is_built` - a content_only topic (Big-O) isn't built either, but
    # it's finished content, not a placeholder, and must not be badged "soon".
    response = client.get("/")
    assert 'class="badge"' not in response.text
    assert response.text.count("soon") == 0


def test_content_only_topic_body_carries_auto_complete_flag():
    response = client.get("/topic/big-o")
    assert 'data-content-only-slug="big-o"' in response.text


def test_built_topic_body_has_no_auto_complete_flag():
    response = client.get("/topic/bubble-sort")
    assert "data-content-only-slug" not in response.text
    assert 'data-topic-slug="bubble-sort"' in response.text


def test_home_page_and_nav_carry_progress_slugs_for_every_topic():
    # Every topic appears exactly once, in the hidden #topic-data block
    # (base.html) - the single DOM data source for search/progress/
    # achievements/locking now that there's no persistent sidebar duplicating
    # it alongside the homepage's own markup.
    response = client.get("/")
    _, by_slug = load_roadmap()
    for slug in by_slug:
        assert response.text.count(f'data-progress-slug="{slug}"') == 1
    topic_response = client.get("/topic/bubble-sort")
    for slug in by_slug:
        assert f'data-progress-slug="{slug}"' in topic_response.text


def test_every_topic_page_has_skip_link_and_main_landmark():
    for slug in ("bubble-sort", "big-o"):
        response = client.get(f"/topic/{slug}")
        assert 'class="skip-link" href="#main-content"' in response.text
        assert 'id="main-content"' in response.text


def test_active_nav_link_has_aria_current():
    response = client.get("/topic/bubble-sort")
    # Exactly one topic-data entry should be marked current - the active
    # topic itself. Search from the id itself since data-blurb text length
    # varies per topic and can push aria-current past any fixed window.
    assert response.text.count('aria-current="page"') == 1
    start = response.text.index('data-progress-slug="bubble-sort"')
    end = response.text.index('>', start)
    assert 'aria-current="page"' in response.text[start:end]


def test_command_palette_has_combobox_listbox_roles():
    response = client.get("/")
    assert 'role="combobox"' in response.text
    assert 'role="listbox"' in response.text
    assert 'aria-controls="cmdk-results"' in response.text


def test_topic_data_category_and_requires_are_well_formed():
    # graph_map.js/achievements.js/progress.js all group topics by the flat
    # `data-category` attribute now (no more nested category containers to
    # walk) - verify every topic carries its real category, and every
    # `requires` slug in the hidden data block actually names a real topic
    # (a typo here would silently produce an unreachable/always-locked node).
    response = client.get("/")
    categories, by_slug = load_roadmap()
    all_slugs = set(by_slug)
    for category in categories:
        for topic in category.topics:
            start = response.text.index(f'data-progress-slug="{topic.slug}"')
            end = response.text.index('>', start)
            tag = response.text[start:end]
            assert f'data-category="{html.escape(category.name)}"' in tag
            requires_attr = tag.split('data-requires="')[1].split('"')[0]
            requires = [s for s in requires_attr.split(',') if s]
            assert set(requires) <= all_slugs, f"{topic.slug} requires unknown slug(s): {requires}"


def test_run_bubble_sort_returns_steps():
    response = client.post("/api/run/bubble_sort", json={"array": [5, 3, 8, 1]})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["array"] == [1, 3, 5, 8]
    assert data["steps"][0]["kind"] == "start"
    assert data["steps"][-1]["kind"] == "done"


def test_run_heap_sort_returns_steps():
    response = client.post("/api/run/heap_sort", json={"array": [5, 3, 8, 1, 9, 2, 7]})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["array"] == [1, 2, 3, 5, 7, 8, 9]
    assert data["steps"][0]["kind"] == "start"
    assert data["steps"][-1]["kind"] == "done"


def test_run_two_pointer_sum_returns_steps():
    response = client.post("/api/run/two_pointer_sum", json={"array": [5, 3, 8, 1, 9, 2, 7], "target": 12})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["found"] is True


def test_run_sliding_window_max_sum_returns_steps():
    response = client.post("/api/run/sliding_window_max_sum", json={"array": [5, 3, 8, 1, 9, 2, 7], "k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["best_sum"] == 18


def test_run_sliding_window_rejects_k_larger_than_array():
    response = client.post("/api/run/sliding_window_max_sum", json={"array": [1, 2, 3], "k": 5})
    assert response.status_code == 422


def test_run_sliding_window_rejects_k_below_one():
    response = client.post("/api/run/sliding_window_max_sum", json={"array": [1, 2, 3], "k": 0})
    assert response.status_code == 422


def test_run_binary_search_returns_result():
    response = client.post("/api/run/binary_search", json={"array": [5, 3, 8, 1], "target": 8})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["found"] is True


def test_run_linked_list_demo_returns_steps():
    response = client.post("/api/run/linked_list_demo", json={"array": [5, 3, 8, 1]})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "list"
    assert data["result"]["values"] == [9, 1, 8, 3]
    assert data["steps"][0]["layout"] == "chain"


def test_run_stack_demo_returns_steps():
    response = client.post("/api/run/stack_demo", json={"array": [1, 2, 3, 4]})
    assert response.status_code == 200
    data = response.json()
    assert data["steps"][0]["layout"] == "stack"


def test_run_queue_demo_returns_steps():
    response = client.post("/api/run/queue_demo", json={"array": [1, 2, 3, 4]})
    assert response.status_code == 200
    data = response.json()
    assert data["steps"][0]["layout"] == "queue"


def test_run_hash_table_demo_returns_steps():
    response = client.post("/api/run/hash_table_demo", json={"array": [10, 3, 17]})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "hash"
    assert data["result"]["bucket_count"] == 7
    assert sorted(data["result"]["values"]) == [3, 10, 17]


def test_run_trie_demo_returns_steps():
    response = client.post("/api/run/trie_demo", json={"words": ["cat", "car", "card", "care", "dog", "do"]})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "tree"
    assert data["result"]["node_count"] == 10


def test_run_trie_rejects_non_alpha_words():
    response = client.post("/api/run/trie_demo", json={"words": ["cat123"]})
    assert response.status_code == 422


def test_run_trie_rejects_too_many_words():
    response = client.post("/api/run/trie_demo", json={"words": [f"w{i}" for i in range(20)]})
    assert response.status_code == 422


def test_run_trie_rejects_empty_word_list():
    response = client.post("/api/run/trie_demo", json={"words": []})
    assert response.status_code == 422


def test_run_union_find_returns_steps():
    response = client.post("/api/run/union_find_demo", json={"edges": "A-B, B-C, D-E, E-F, F-G, A-D, B-G"})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "tree"
    assert data["result"]["sets"] == 1


def test_run_union_find_rejects_malformed_edges():
    response = client.post("/api/run/union_find_demo", json={"edges": "A--B"})
    assert response.status_code == 422


def test_run_n_queens_returns_steps():
    response = client.post("/api/run/n_queens", json={"n": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "dp"
    assert data["result"]["solutions"] == 2


def test_run_n_queens_rejects_n_above_max():
    response = client.post("/api/run/n_queens", json={"n": 6})
    assert response.status_code == 422


def test_run_n_queens_rejects_n_below_one():
    response = client.post("/api/run/n_queens", json={"n": 0})
    assert response.status_code == 422


def test_run_bst_ops_returns_steps():
    response = client.post("/api/run/bst_ops", json={"array": [5, 3, 8, 1, 4], "target": 8})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "tree"
    assert data["result"]["node_count"] == 4


def test_run_tree_traversal_demo_returns_steps():
    response = client.post("/api/run/tree_traversal_demo", json={"array": [5, 3, 8]})
    assert response.status_code == 200
    data = response.json()
    assert data["steps"][0]["nodes"] == []


def test_run_binary_heap_demo_returns_steps():
    response = client.post("/api/run/binary_heap_demo", json={"array": [5, 3, 8, 1]})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "tree"


def test_run_tree_family_rejects_oversized_input():
    response = client.post("/api/run/tree_traversal_demo", json={"array": list(range(30))})
    assert response.status_code == 422


def test_run_bfs_demo_returns_steps():
    response = client.post("/api/run/bfs_demo", json={"edges": "A-B, B-C", "start": "A"})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "graph"
    assert data["result"]["node_count"] == 3


def test_run_dijkstra_demo_returns_steps():
    response = client.post("/api/run/dijkstra_demo", json={"edges": "A-B:4, B-C:2", "start": "A"})
    assert response.status_code == 200


def test_run_topological_sort_demo_returns_steps():
    response = client.post("/api/run/topological_sort_demo", json={"edges": "A-B, B-C"})
    assert response.status_code == 200


def test_run_graph_rejects_unknown_start_node():
    response = client.post("/api/run/bfs_demo", json={"edges": "A-B, B-C", "start": "Z"})
    assert response.status_code == 422


def test_run_graph_rejects_malformed_edges():
    response = client.post("/api/run/bfs_demo", json={"edges": "A--B", "start": "A"})
    assert response.status_code == 422


def test_run_graph_rejects_too_many_nodes():
    edges = ", ".join(f"N{i}-N{i + 1}" for i in range(20))
    response = client.post("/api/run/topological_sort_demo", json={"edges": edges})
    assert response.status_code == 422


def test_run_fibonacci_memo_returns_steps():
    response = client.post("/api/run/fibonacci_memo", json={"n": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["family"] == "dp"
    assert data["result"]["value"] == 55


def test_run_knapsack_returns_steps():
    response = client.post("/api/run/knapsack", json={"capacity": 10, "weights": [2, 3, 4, 5], "values": [3, 4, 5, 6]})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["best_value"] > 0


def test_run_lcs_returns_steps():
    response = client.post("/api/run/lcs", json={"a": "ABCBDAB", "b": "BDCABA"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["length"] == 4


def test_run_fibonacci_rejects_too_large_n():
    response = client.post("/api/run/fibonacci_memo", json={"n": 999})
    assert response.status_code == 422


def test_run_knapsack_rejects_mismatched_weights_and_values():
    response = client.post("/api/run/knapsack", json={"capacity": 10, "weights": [1, 2], "values": [1]})
    assert response.status_code == 422


def test_run_lcs_rejects_empty_string():
    response = client.post("/api/run/lcs", json={"a": "", "b": "ABC"})
    assert response.status_code == 422


def test_run_list_family_rejects_oversized_input():
    response = client.post("/api/run/stack_demo", json={"array": list(range(50))})
    assert response.status_code == 422


def test_run_unknown_algo_404s():
    response = client.post("/api/run/not_a_real_algo", json={"array": [1, 2, 3]})
    assert response.status_code == 404


def test_run_rejects_oversized_array():
    response = client.post("/api/run/bubble_sort", json={"array": list(range(200))})
    assert response.status_code == 422


def test_run_rejects_empty_array():
    response = client.post("/api/run/bubble_sort", json={"array": []})
    assert response.status_code == 422


def test_every_built_topic_has_a_matching_registry_entry():
    raw = yaml.safe_load(TOPICS_YAML.read_text(encoding="utf-8"))
    for entry in raw:
        if entry.get("status") == "built":
            algo_key = entry.get("algo_key")
            assert algo_key, f"{entry['slug']} is built but declares no algo_key"
            assert algo_key in ALGORITHMS, f"{entry['slug']} references unregistered algo_key '{algo_key}'"


def test_every_topic_markdown_file_exists():
    raw = yaml.safe_load(TOPICS_YAML.read_text(encoding="utf-8"))
    for entry in raw:
        md_path = CONTENT_DIR / entry["markdown"]
        if entry.get("status") in ("built", "content_only"):
            assert md_path.exists(), f"{entry['slug']} is {entry['status']} but {entry['markdown']} is missing"
