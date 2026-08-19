import pytest

from app.algorithms import searching


def test_linear_search_finds_present_value():
    arr = [5, 3, 8, 1, 9, 2, 7]
    steps = list(searching.linear_search(arr, 8))
    assert steps[-1]["kind"] == "found"
    assert steps[-1]["indices"]["found"] == arr.index(8)


def test_linear_search_reports_missing_value():
    steps = list(searching.linear_search([1, 2, 3], 99))
    assert steps[-1]["kind"] == "not_found"
    assert steps[-1]["indices"]["found"] is None


def test_binary_search_finds_present_value_in_unsorted_input():
    arr = [5, 3, 8, 1, 9, 2, 7]
    steps = list(searching.binary_search(arr, 8))
    assert steps[-1]["kind"] == "found"
    found_index = steps[-1]["indices"]["found"]
    assert steps[-1]["array"][found_index] == 8
    assert steps[-1]["array"] == sorted(arr)


def test_binary_search_reports_missing_value():
    steps = list(searching.binary_search([1, 2, 3, 4, 5], 99))
    assert steps[-1]["kind"] == "not_found"


@pytest.mark.parametrize("target_pos", range(7))
def test_binary_search_finds_every_position(target_pos):
    arr = [1, 3, 5, 7, 9, 11, 13]
    steps = list(searching.binary_search(arr, arr[target_pos]))
    assert steps[-1]["kind"] == "found"
    assert steps[-1]["array"][steps[-1]["indices"]["found"]] == arr[target_pos]
