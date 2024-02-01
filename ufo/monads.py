from typing import Any, Callable, Generic
from typing import List as ListType
from typing import Optional, Type, TypeVar, Union
from copy import deepcopy

T = TypeVar("T")
U = TypeVar("U")


class Monad(Generic[T]):
    """
    Identity monad (also the parent class for all other monads).

    No additional work is handled on function calls, apart from returning
    a new monad with an updated result.

    Can be used like so:

    ```python
    def make_loud(x:str) -> str:
        return x.upper()

    x = Monad("hello world!") >> make_loud

    print(x.value)
    # prints out "HELLO WORLD!"
    ```
    """
    def __init__(self: Any, value: T) -> None:
        """
        Initialise a monad with the given value
        """
        self.value: T = value

    def bind(self, func) -> "Monad":
        """
        Method to apply function to value of Monad.
        Returns a monad with the updated value.

        Example:
        ```python
        Monad(2).bind(lambda x: x+1) == Monad(3)
        ```

        Can be aliased with `>>` symbol:
        ```python
        (Monad(2) >> (lambda x: x+1)) == Monad(3)
        """
        return Monad(func(self.value))

    def __rshift__(self, other) -> "Monad":
        """
        Dunder method to alias bind into >>
        """
        return self.bind(other)

    def unwrap(self) -> T:
        """
        Return only the value of the monad without wrapping
        it.

        ```python
        Monad(4).unwrap() == 4
        ```
        """
        return self.value

    def __str__(self) -> str:
        """
        String representation
        """
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self) -> str:
        """
        For repls
        """
        return self.__str__()


class Maybe(Monad, Generic[T]):
    """
    Monad to handle None values.

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


class List(Monad, Generic[T]):
    """
    Monad to apply function to all items in list.

    Write functions as if they act on a single value.

    Example:
    ```python
    x = (
        List([1, 3, 7])
        >> (lambda x: x + 1)
        >> (lambda x: x / 2)
    )
    # x will evaluate to List([1, 2, 4])
    """
    def __init__(self: Any, value: ListType[T]) -> None:
        """
        Initialise a monad with the given list
        """
        self.value: ListType[T] = value

    def bind(self, func: Callable) -> "List":
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
        return List([func(x) for x in self.value])

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
        return List([i for i in self.value if func(i)])

    def unwrap(self) -> ListType[T]:
        """
        Return only the value of the monad without wrapping
        it.

        ```python
        List([4]).unwrap() == [4]
        ```
        """
        return self.value


class Result(Monad, Generic[T]):
    """
    Monad to handle errors. Handle exceptions on unwrap:

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
        """
        if self.exception:
            return self
        value_copy = deepcopy(self.value)
        try:
            return Result(func(self.value))
        except Exception as exception:
            error_monad = Result(None, exception)
            error_monad._value_to_recover = value_copy
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
            value_copy = deepcopy(self._value_to_recover)
            try:
                return Result(func(self._value_to_recover))
            except Exception as exception:
                error_monad = Result(None, exception)
                error_monad._value_to_recover = value_copy
                return error_monad
        return self
        

    def __str__(self) -> str:
        """
        Custom string representation
        """
        return f"{self.__class__.__name__}({self.exception or self.value})"
