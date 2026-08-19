from app.algorithms import hashing


def test_inserts_every_value_into_the_correct_bucket():
    arr = [10, 3, 17, 24]  # 10%7=3, 3%7=3, 17%7=3, 24%7=3 -> all collide into bucket 3
    steps = list(hashing.hash_table_demo(arr, table_size=7))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    final_buckets = steps[-1]["buckets"]
    assert len(final_buckets) == 7
    bucket_3_values = [n["value"] for n in final_buckets[3]["nodes"]]
    assert bucket_3_values == [10, 3, 17, 24]
    for i in (0, 1, 2, 4, 5, 6):
        assert final_buckets[i]["nodes"] == []


def test_collision_is_flagged_when_a_bucket_is_reused():
    arr = [10, 3]  # both hash to bucket 3
    steps = list(hashing.hash_table_demo(arr, table_size=7))
    collision_steps = [s for s in steps if s["kind"] == "collision"]
    assert len(collision_steps) == 1
    assert collision_steps[0]["active_bucket"] == 3


def test_no_collision_when_values_spread_across_buckets():
    arr = [0, 1, 2, 3, 4, 5, 6]  # each hashes to a distinct bucket
    steps = list(hashing.hash_table_demo(arr, table_size=7))
    assert not any(s["kind"] == "collision" for s in steps)


def test_handles_empty_input():
    steps = list(hashing.hash_table_demo([], table_size=7))
    assert steps[-1]["kind"] == "done"
    assert all(bucket["nodes"] == [] for bucket in steps[-1]["buckets"])
