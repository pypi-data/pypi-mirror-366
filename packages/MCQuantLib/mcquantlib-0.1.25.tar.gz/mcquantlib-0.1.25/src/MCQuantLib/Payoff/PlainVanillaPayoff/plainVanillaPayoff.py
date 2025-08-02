import numpy as np
from numbers import Real
from typing import Union
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.decoratorTool import ValueAsserter

class PlainVanillaPayoff(Payoff):
    """
    For call option, if underlyingPrice > strike, return underlyingPrice - strike, else return 0.
    For put option, if underlyingPrice < strike, return strike - underlyingPrice, else return 0.
    """
    @staticmethod
    @ValueAsserter(argIndexList=[1], argKeyList=['optionType'], value={1, -1})
    def plainVanillaPayoff(underlyingPrice: Union[np.ndarray, Real], optionType: int, strike: Real) -> Union[np.ndarray, Real]:
        return np.maximum(underlyingPrice - strike, 0) if optionType == 1 else np.maximum(strike - underlyingPrice, 0)

    def __init__(self, optionType: int, strike: Real) -> None:
        super(PlainVanillaPayoff, self).__init__(PlainVanillaPayoff.plainVanillaPayoff, optionType=optionType, strike=strike)
