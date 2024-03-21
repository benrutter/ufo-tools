"""
Tests for ufo.containers
"""
import pytest

from ufo_tools import containers

def test_container_equality_matches_container_type_and_values():
    assert containers.Result(3) != containers.Container(3)
    assert containers.Container(4) != containers.Container(3)
    assert containers.Container(4) == containers.Container(4)

def test_container_provides_string_dunder():
    assert str(containers.Container(3)) == "Container(3)"

def test_container_provides_repr_dunder():
    assert containers.Container(3).__repr__() == "Container(3)"

def test_container_then_binds_with_given_function():
    actual = (
        containers.Container(3)
        .then(lambda x: x + 1)
        .then(lambda x: x / 2)
    )
    assert actual == containers.Container(2)

def test_container_then_allows_positional_int():
    def cool(x, y):
        return y
    assert containers.Container(2).then((cool, 1), 45) == containers.Container(2)

def test_container_then_allows_keyword():
    def cool(x, y):
        return y
    assert containers.Container(2).then((cool, "y"), 45) == containers.Container(2)

def test_unwrap_produces_contained_value():
    assert containers.Container(3).unwrap() == 3

def test_maybe_handles_nones_with_then():
    assert containers.Maybe(None).then(lambda x: x + 3) == containers.Maybe(None)

def test_maybe_handles_non_nones_like_then():
    actual = containers.Maybe(3).then(lambda x: x + 2).unwrap()
    expected = containers.Container(3).then(lambda x: x + 2).unwrap()
    assert actual == expected

def test_maybe_offers_default_in_unwrap():
    assert containers.Maybe(None).unwrap(4) == 4

def test_array_maps_over_items():
    actual = containers.Array(i for i in range(2)).then(lambda x: x + 1)
    assert actual == containers.Array(1, 2)

def test_filter_removes_expected_from_array():
    assert containers.Array(2, 3).filter(lambda x: x == 3) == containers.Array(3)

def test_reduce_iterates_as_expected():
    assert containers.Array(1, 2).reduce(lambda x, y: x + y).unwrap() == 3

def test_reduce_passes_down_initial():
    assert containers.Array(1, 2).reduce(lambda x, y: x + y, 1).unwrap() == 4

def test_array_provides_customer_str_dunder():
    assert str(containers.Array(3, 4)) == "Array(3, 4)"
    
def test_result_holds_error_state_rather_than_immediately_throw():
    containers.Result(3).then(lambda x: x / 0)
    assert True

def test_result_unwrap_throws_held_error_state():
    with pytest.raises(ZeroDivisionError):
        containers.Result(3).then(lambda x: x / 0).unwrap()

def test_result_unwrap_can_default_error_to_value():
    assert containers.Result(3).then(lambda x: x / 0).then(lambda x: x + 3).unwrap(4) == 4

def test_result_unwrap_can_match_specific_errors():
    assert containers.Result(3).then(lambda x: x / 0).unwrap(4, ZeroDivisionError) == 4
    with pytest.raises(ZeroDivisionError):
        containers.Result(3).then(lambda x: x / 0).unwrap(4, AssertionError)

def test_result_unwrap_behaves_as_normal_for_non_error_cases():
    assert containers.Result(3).unwrap() == 3

def test_recover_can_regain_last_non_error_state():
    actual = containers.Result(3).then(lambda x: x / 0).recover(lambda x: x - 1)
    assert actual == containers.Result(2)

def test_recover_returns_new_error_container_if_fails():
    actual = containers.Result(3).then(lambda x: x/0).recover(lambda x: x/0)
    assert actual.in_error_state()

def test_recover_just_returns_self_if_no_error_state():
    assert containers.Result(3).recover(lambda x: x+1).unwrap() == 3

def test_in_error_state_return_bool_based_on_error_state():
    assert containers.Result(3).in_error_state() is False
    assert containers.Result(3).then(lambda x: x/0).in_error_state() is True
    
def test_result_provides_custom_string_dunder():
    assert str(containers.Result(3)) == "Result(3)"
    assert str(containers.Result(1).then(lambda x: x/0)) == "Result(division by zero)"
