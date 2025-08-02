import numpy as np
from numbers import Real
from typing import Union, Callable, Any
from numpy.typing import ArrayLike

class Payoff(object):
    """
    This is the payoff base class of any payoff structure. It defines the basic
    operation of payoff, including + - * /.

    This class accepts a function, whose first argument
    has to be a numpy.ndarray that is underlying price or underlying rtn. The call to instance
    of Payoff class will be forwarded into this function.

    This difference between this class and QuantLib Payoff class is that this one use numpy to
    assure speed, while QuantLib does not. This class is specialized in Monte Carlo, suitable for
    multi-paths simulation.
    """

    def __init__(self, func: Callable[[Union[np.ndarray, Real], Any, ...], Union[np.ndarray, Real]], *args, **keywords) -> None:
        self.func = func
        self.args = args
        self.keywords = keywords

    def functor(self, functor: Callable[[Any, Any], Any], other: Callable[[Union[np.ndarray, Real]], Union[np.ndarray, Real]]) -> 'Payoff':
        def f(assetPrice: Union[np.ndarray, Real], *args, **kwargs) -> Union[np.ndarray, Real]:
            return functor(self(assetPrice), other(assetPrice))
        return Payoff(f, *self.args, **self.keywords)

    def monoid(self, monoid: Callable[[Any], Any]) -> 'Payoff':
        def f(assetPrice: Union[np.ndarray, Real], *args, **kwargs) -> Union[np.ndarray, Real]:
            return monoid(self(assetPrice))
        return Payoff(f, *self.args, **self.keywords)

    def monad(self, monad: Callable[[Any], Any]) -> 'Payoff':
        def f(assetPrice: Union[ArrayLike, Real], *args, **kwargs) -> Union[np.ndarray, Real]:
            return self(monad(assetPrice))
        return Payoff(f, *self.args, **self.keywords)

    def toLog(self, spotPrice: Real) -> 'Payoff':
        """Convert the payoff function to log."""
        return self.monad(lambda x: np.exp(x) * spotPrice)

    def __call__(self, assetPrice: Union[np.ndarray, Real]) -> Union[np.ndarray, Real]:
        return self.func(assetPrice, *self.args, **self.keywords)

    def __add__(self, other) -> 'Payoff':
        assert isinstance(other, Payoff)
        return self.functor(lambda x, y: x+y, other)

    def __sub__(self, other) -> 'Payoff':
        assert isinstance(other, Payoff)
        return self.functor(lambda x, y: x-y, other)

    def __neg__(self) -> 'Payoff':
        return self.monoid(lambda x: -1 * x)

    def __rmul__(self, scalar: Real) -> 'Payoff':
        return self.monoid(lambda x: scalar * x)

    __mul__ = __rmul__
