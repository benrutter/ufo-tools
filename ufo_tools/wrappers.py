"""
Useful wrappers for
decorating functions to
gain extra features.
"""
from copy import deepcopy
from functools import wraps
from typing import Any, Callable
from warnings import warn


def mutation_free(func: Callable) -> Callable:
    """
    Guard against mutation by passing in only deep-copies of arguments
    to functions.

    Take the following function which accidently introduces side effects:
    ```python
    def print_appended(some_list: list, x: Any):
        some_list.append(x)
        print(some_list)

    some_list = [1, 2, 3]
    print_appended(some_list, 4)
    >> [1, 2, 3, 4]

    # now, some_list has been mutated:
    print(some_list)
    >> [1, 2, 3, 4]
    ```
    You can guard against mutation by using the mutation_free wrapper:
    ```python
    @mutation_free
    def print_appended(some_list: list, x: Any):
        some_list.append(x)
        print(some_list)

    some_list = [1, 2, 3]
    print_appended(some_list, 4)
    >> [1, 2, 3, 4]

    print(some_list)
    >> [1, 2, 3]
    ```

    This *won't* prevent functions from mutating global variables by using the
    global keyword. Additionally, because it makes deepcopies of all function
    arguments, it may introduce performance trade-offs in some situations where
    function are taking large objects as arguments.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        copy_kwargs = {deepcopy(k): deepcopy(v) for k, v in kwargs.items()}
        copy_args = [deepcopy(i) for i in args]
        return func(*copy_args, **copy_kwargs)

    return wrapped_func


def coerce_into(value: Any, *exceptions) -> Callable:
    """
    Return wrapper for function to convert exceptions matching type into
    specific values:

    ```python
    @coerce_into("default", FileNotFound, KeyError)
    def get_user_setting(expected_directory: str) -> str:
        with open(expected_directory) as file:
            config = json.load(file.read())
        return config["some_setting"]
    ```
    """

    def coerce_wrapper(func_to_wrap: Callable) -> Callable:
        @wraps(func_to_wrap)
        def coercing_func(*args, **kwargs):
            try:
                return func_to_wrap(*args, **kwargs)
            except Exception as exception:
                if len(exceptions) == 0 or type(exception) in exceptions:
                    return value
                raise exception

        return coercing_func

    return coerce_wrapper


def deprecated(func: Callable) -> Callable:
    """
    This decorator can be used to mark functions as deprecated, it
    will emit a warning whenever the function is called.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        warn(
            f"{func.__name__} has been marked as deprecated",
            DeprecationWarning,
        )
        return func(*args, **kwargs)

    return wrapped_func


def retry(retries: int, *exceptions) -> Callable:
    """
    Return wrapper for function to retry on any (if not given) or specific
    exception types.

    After given number of retries, exception will be raised.

    ```python
    @retry(3, AssertionError, ValueError)
    def cool():
        print("cool!")
        assert False, "yikes!"()
    # ^^ With the wrapper, this function will print "cool!"
    #    three times before crashing
    ```

    *Friendly warning!* 👽
    if you're retrying your function probably has side effects, watch out
    that function failures and retries aren't doing something like
    writing to a database multiple times.
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            for attempt in range(retries, 0, -1):
                try:
                    return func(*args, **kwargs)
                except Exception as exception:
                    if exceptions and type(exception) not in exceptions:
                        raise exception
                    last_exception = exception
            raise last_exception

        return wrapped_func

    return wrapper
