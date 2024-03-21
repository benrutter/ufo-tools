"""
tests for ufo_tools.wrappers
"""
import pytest

from ufo_tools import wrappers


def test_mutation_free_stops_mutations():
    some_list = [2]

    @wrappers.mutation_free
    def mutate_things(thing):
        thing.append(3)

    mutate_things(some_list)
    assert len(some_list) == 1


def test_coerce_into_masks_errors_to_values():
    @wrappers.coerce_into(9)
    def raise_error():
        assert False

    assert raise_error() == 9


def test_coerce_into_matches_given_exceptions():
    @wrappers.coerce_into(9, AssertionError)
    def raise_error():
        assert False

    @wrappers.coerce_into(9, ImportError)
    def actually_raise_error():
        assert False

    assert raise_error() == 9
    with pytest.raises(AssertionError):
        actually_raise_error()


def test_deprecated_warns():
    @wrappers.deprecated
    def say_hello():
        print("hello world!")

    with pytest.warns(DeprecationWarning):
        say_hello()


def test_retry_tries_n_times():
    @wrappers.retry(3)
    def keep_trying(counter=[1, 2]):
        if len(counter) == 0:
            return 7
        counter.pop()
        assert False

    assert keep_trying() == 7

    @wrappers.retry(2)
    def try_again(counter=[1, 2]):
        if len(counter) == 0:
            return 7
        counter.pop()
        assert False

    with pytest.raises(AssertionError):
        try_again()


def test_retry_masks_only_given_errors():
    @wrappers.retry(3, AssertionError)
    def keep_trying(counter=[1, 2]):
        if len(counter) == 0:
            return 7
        counter.pop()
        assert False

    assert keep_trying() == 7

    @wrappers.retry(2, ZeroDivisionError)
    def try_again(counter=[1, 2]):
        if len(counter) == 0:
            return 7
        counter.pop()
        assert False

    with pytest.raises(AssertionError):
        try_again()
