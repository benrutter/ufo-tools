from typing import Callable
from copy import deepcopy
from functools import wraps

def pure(func: Callable) -> Callable:
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        copy_kwargs = {deepcopy(k): deepcopy(v) for k, v in kwargs.items()}
        copy_args = [deepcopy(i) for i in args]
        return func(*copy_args, **copy_kwargs)
    return wrapped_func

