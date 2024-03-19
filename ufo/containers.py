from typing import Any, Callable, Generic, Generator
from typing import List as ListType
from typing import Optional, Type, TypeVar, Union
from functools import reduce, partial

T = TypeVar("T")
U = TypeVar("U")


class Simple(Generic[T]):
    """
    Simple identity container (also the parent class for all other containers)

    No additional work is handled on function calls, apart from returning
    a new monad with an updated result.

    Can be used like so:

    ```python
    def make_loud(x:str) -> str:
        return x.upper()

    x = Simple("hello world!") >> make_loud

    print(x.value)
    # prints out "HELLO WORLD!"
    ```
    """
    def __init__(self: Any, value: T) -> None:
        """
        Initialise a container with the given value
        """
        self.value: T = value

    def bind(self, func, **kwargs) -> "Simple":
        """
        Method to apply function to value of Monad.
        Returns a container with the updated value.

        Example:
        ```python
        Simple(2).bind(lambda x: x+1) == Simple(3)
        ```

        Can be aliased with `>>` symbol:
        ```python
        (Simple(2) >> (lambda x: x+1)) == Simple(3)
        ```

        Additional keyword arguments for function can be provided:
        ```python
        def add_to(x:int, y:int) -> int:
            return x + y

        Simple(4).bind(add_to, y=1) == Simple(5)
        ```
        (note that this isn't possible using `>>` alias)
        """
        return Simple(partial(func, **kwargs)(self.value))

    def __rshift__(self, other) -> "Simple":
        """
        Dunder method to alias bind into >>
        """
        return self.bind(other)

    def unwrap(self) -> T:
        """
        Return only the value of the Simple without wrapping
        it.

        ```python
        Simple(4).unwrap() == 4
        ```
        """
        return self.value

    def __eq__(self, other) -> bool:
        """
        Equality operator, true if containers are of same type
        and values are equal.
        """
        if not isinstance(other, type(self)):
            return False
        return self.value == other.value

    def __str__(self) -> str:
        """
        String representation
        """
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self) -> str:
        """
        Representaion for REPLs
        """
        return self.__str__()


class Maybe(Simple, Generic[T]):
    """
    Container to handle None values.

    Write functions as if they can't recieve None values.
    If Monad value is None, it will skip execution of function
    and remain as None.

    None example:
    ```python
    Maybe(None) >> (lambda x: x + 4)  # will remain None
    ```
    """
    def bind(self, func: Callable) -> "Maybe":
        """
        Execute function on value, unless None
        (in which case return None monad)
        """
        if self.value is None:
            return Maybe(None)
        return Maybe(func(self.value))

    def unwrap_or(self, value: U) -> Union[T, U]:
        """
        Return container value, unless that is None
        in which case return given value.

        Example:
        ```python
        Maybe(None).unwrap_or(8) == 8
        ```
        """
        if self.value is None:
            return value
        return self.value


class List(Simple, Generic[T]):
    """
    Monad to apply function to all items in list.

    Write functions as if they act on a single value.

    Example:
    ```python
    x = (
        List(1, 3, 7)
        >> (lambda x: x + 1)
        >> (lambda x: x / 2)
    )
    # x will evaluate to List([1, 2, 4])
    """
    def __init__(self: Any, *values: T) -> None:
        """
        Initialise a monad with the given list
        """
        if len(values) == 1 and isinstance(values[0], Generator):
            self.value: ListType[T] = list(values[0])
        else:
            self.value: ListType[T] = list(values)

    def bind(self, func: Callable, **kwargs) -> "List":
        """
        Map function on every element of list:

        ```python
        def make_exciting(text: str) -> str:
            return test.upper() + "!!!"

        fun_stuff = (
            List(["hats", "cats", "bats"])
            >> make_exciting
        ).unwrap()

        fun_stuff == ["HATS!!!", "CATS!!!", "BATS!!!"]
        """
        return List(partial(func, **kwargs)(x) for x in self.value)

    def filter(self, func: Callable) -> "List":
        """
        Filter list to only elements with true return:

        ```python
        x = (
            List([1, 2, 3, 4])
            .filter(lambda x: x % 2 == 0)
        ).unwrap()

        x == [2, 4]
        """
        return List(i for i in self.value if func(i))

    def unwrap(self) -> ListType[T]:
        """
        Return only the value of the container without wrapping
        it.

        ```python
        List([4]).unwrap() == [4]
        ```
        """
        return self.value

    def reduce(self, func: Callable[[T, U], U]) -> Simple[U]:
        """
        Applies reduce over list, returning result
        in a Simple container.

        Optional `initial` argument to pass down into reduce.
        """
        return Simple(reduce(func, self.value))

    def __str__(self) -> str:
        """
        String representation
        """
        return f"{self.__class__.__name__}({', '.join(str(i) for i in self.value)})"


class Result(Simple, Generic[T]):
    """
    Container to handle errors. Handle exceptions on unwrap:

    ```python
    x = (
        Result(3)
        >> (lamba x / 0)
    )

    x.value == None
    isinstance(x.exception, ZeroDivisionError)
    x.unwrap_or(4) == 4
    ```
    """
    def __init__(self, value: T, exception: Optional[Type[Exception]] = None):
        """
        Create Result monad with value and exception
        (one of which will always be None)
        """
        self.value: T = value
        self.exception = exception
        self._value_to_recover = None

    def bind(self, func) -> "Result":
        """
        Execute function on value, if error is raised,
        returned Monad will have value of "None" and an exception.

        Otherwise, exception will be None, and value will be return.

        If exception already exists, function won't be executed.

        Note, that this container does not in itself protect you from
        mutation, if you're function mutates the value into a
        non-recoverable state, this could cause errors.

        To avoid mutation, see mutation_free wrapper in metafunctions.
        """
        if self.exception:
            return self
        to_recover = self.value
        try:
            return Result(func(self.value))
        except Exception as exception:
            error_monad = Result(None, exception)
            error_monad._value_to_recover = to_recover
            return error_monad

    def unwrap(self) -> T:
        """
        If exception is raised, will raise exception.
        Otherwise will evaluate to value.
        """
        if self.exception:
            raise self.exception
        return self.value

    def unwrap_or(self, value: U) -> Union[T, U]:
        """
        If exception is raised, will default to given value.
        """
        if self.exception:
            return value
        return self.value

    def recover(self, func) -> "Result":
        """
        If Result is in error state, apply function to last
        non-error state value.

        Example:
        ```python
        x = (
            Result(3)
            .bind(lamba x: x / 0)
            .recover(lambda x: x + 1)
        )
        x == 4  # <- recover function applied to 3
        ```
        """
        if self.exception:
            to_recover = self._value_to_recover
            try:
                return Result(func(self._value_to_recover))
            except Exception as exception:
                error_monad = Result(None, exception)
                error_monad._value_to_recover = to_recover
                return error_monad
        return self

    def in_error_state(self) -> bool:
        """
        Function to return bool based on whether container is
        in error state from previous error.

        Returns True if in error state, and False otherwise.
        """
        if self.exception:
            return True
        return False

    def __str__(self) -> str:
        """
        Custom string representation
        """
        return f"{self.__class__.__name__}({self.exception or self.value})"
