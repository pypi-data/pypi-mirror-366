import numpy as np
from typing import Callable, Any

class Path(object):
    """This class defines how the barrier stop the path. It is like a filter of path array."""
    def __init__(self, func: Callable[[np.ndarray, Any, ...], np.ndarray], *args, **keywords) -> None:
        self.func = func
        self.args = args
        self.keywords = keywords

    def switch(self, func: Callable[[np.ndarray, Any, ...], np.ndarray]) -> 'Path':
        """Keep current args and kwargs, change func into a new one."""
        return Path(func, *self.args, **self.keywords)

    def functor(self, functor: Callable[[np.ndarray, np.ndarray], np.ndarray], other: Callable[[np.ndarray], np.ndarray]) -> 'Path':
        """functor can be used only if self.func return an array, rather than tuple."""
        def f(path: np.ndarray, *args, **kwargs) -> np.ndarray:
            return functor(self(path), other(path))
        return Path(f, *self.args, **self.keywords)

    def monoid(self, monoid: Callable[[np.ndarray], np.ndarray]) -> 'Path':
        """monoid can be used only if self.func return an array, rather than tuple."""
        def f(path: np.ndarray, *args, **kwargs) -> np.ndarray:
            return monoid(self(path))
        return Path(f, *self.args, **self.keywords)

    def __call__(self, path: np.ndarray) -> np.ndarray:
        return self.func(path, *self.args, **self.keywords)

    def __add__(self, other: 'Path') -> 'Path':
        """add can be used only if self.func return an array, rather than tuple."""
        return self.functor(lambda x, y: x | y, other)

    def __sub__(self, other: 'Path') -> 'Path':
        """sub can be used only if self.func return an array, rather than tuple."""
        return self.functor(lambda x, y: x | (np.logical_not(y)), other)

    def __neg__(self) -> 'Path':
        """neg can be used only if self.func return an array, rather than tuple."""
        return self.monoid(lambda x: np.logical_not(x))

    def __mul__(self, other: 'Path') -> 'Path':
        """mul can be used only if self.func return an array, rather than tuple."""
        return self.functor(lambda x, y: x & y, other)


