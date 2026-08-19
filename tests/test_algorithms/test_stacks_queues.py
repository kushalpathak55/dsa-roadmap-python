from app.algorithms import stacks_queues


def test_stack_push_then_pop_half_is_lifo():
    arr = [1, 2, 3, 4]
    steps = list(stacks_queues.stack_demo(arr))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    push_steps = [s for s in steps if s["kind"] == "push"]
    assert [s["nodes"][-1]["value"] for s in push_steps] == arr

    # pops half of 4 = 2 pops; LIFO order means the last pushed value (4) comes off first
    peeked_before_pop = [s["nodes"][-1]["value"] for s in steps if s["kind"] == "peek"]
    assert peeked_before_pop == [4, 3]


def test_stack_layout_and_schema():
    steps = list(stacks_queues.stack_demo([1, 2]))
    for step in steps:
        assert step["layout"] == "stack"
        assert "top" in step["pointers"]


def test_queue_enqueue_then_dequeue_half_is_fifo():
    arr = [1, 2, 3, 4]
    steps = list(stacks_queues.queue_demo(arr))
    assert steps[0]["kind"] == "start"
    assert steps[-1]["kind"] == "done"

    peek_values = [s["nodes"][0]["value"] for s in steps if s["kind"] == "peek"]
    assert peek_values == [1, 2]  # FIFO: earliest enqueued (1) comes off first


def test_queue_layout_and_schema():
    steps = list(stacks_queues.queue_demo([1, 2]))
    for step in steps:
        assert step["layout"] == "queue"
        assert "front" in step["pointers"] and "rear" in step["pointers"]


def test_empty_input_is_handled():
    assert list(stacks_queues.stack_demo([]))[-1]["kind"] == "done"
    assert list(stacks_queues.queue_demo([]))[-1]["kind"] == "done"
