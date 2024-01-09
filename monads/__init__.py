class Monad:
    def __init__(self, value):
        self.value = value

    def bind(self, func):
        return Monad(func(self.value))

    def pipe(self, funcs):
        result = self
        for func in funcs:
            result = self.bind(func)
        return result

    def __or__(self, other):
        return self.bind(other)

    def unwrap(self):
        return self.value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self):
        return self.__str__()

class Maybe(Monad):
    def bind(self, func):
        if self.value is None:
            return Maybe(None)
        return Maybe(func(self.value))

class ListMonad(Monad):
    def bind(self, func):
        return ListMonad([func(x) for x in self.value])

    def filter(self, func):
        return ListMonad([i for i in self.value if func(i)])

class Result(Monad):
    def __init__(self, value, exception = None):
        self.value = value
        self.exception = exception

    def bind(self, func):
        if self.exception:
            return self
        try:
            return Result(func(self.value))
        except Exception as exception:
            return Result(self.value, exception)

    def unwrap(self):
        if self.exception:
            raise self.exception
        return self.value

    def __str__(self):
        return f"{self.__class__.__name__}({self.exception or self.value})"
