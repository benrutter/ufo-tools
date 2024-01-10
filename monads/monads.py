from typing import Any, Callable, Generic
from typing import List as ListType
from typing import Optional, Type, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class Monad(Generic[T]):
    def __init__(self: Any, value: T) -> None:
        self.value: T = value

    def bind(self, func) -> "Monad":
        return Monad(func(self.value))

    def pipe(self, *funcs) -> "Monad":
        result = self
        for func in funcs:
            result = self.bind(func)
        return result

    def __rshift__(self, other) -> "Monad":
        return self.bind(other)

    def unwrap(self) -> T:
        return self.value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Maybe(Generic[T], Monad):
    def bind(self, func: Callable) -> "Maybe":
        if self.value is None:
            return Maybe(None)
        return Maybe(func(self.value))


class List(Generic[T], Monad):
    def __init__(self: Any, value: ListType[T]) -> None:
        self.value: ListType[T] = value

    def bind(self, func: Callable) -> "List":
        return List([func(x) for x in self.value])

    def filter(self, func: Callable) -> "List":
        return List([i for i in self.value if func(i)])

    def unwrap(self) -> ListType[T]:
        return self.value


class Result(Generic[T], Monad):
    def __init__(self, value: T, exception: Optional[Type[Exception]] = None):
        self.value: T = value
        self.exception = exception

    def bind(self, func):
        if self.exception:
            return self
        try:
            return Result(func(self.value))
        except Exception as exception:
            return Result(None, exception)

    def unwrap(self) -> T:
        if self.exception:
            raise self.exception
        return self.value

    def unwrap_or(self, value: U) -> Union[T, U]:
        if self.exception:
            return value
        return self.value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.exception or self.value})"
