import numpy as np
from numbers import Real
from typing import Union
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.decoratorTool import ValueAsserter

class GapPayoff(Payoff):
    """
    For call option, if underlyingPrice > strike, return underlyingPrice - strikePayoff, else return 0.
    For put option, if underlyingPrice < strike, return strikePayoff - underlyingPrice, else return 0.
    """
    @staticmethod
    @ValueAsserter(argIndexList=[1], argKeyList=['optionType'], value={1, -1})
    def gapPayoff(underlyingPrice: Union[np.ndarray, Real], optionType: int, strike: Real, strikePayoff: Real) -> Union[np.ndarray, Real]:
        payoff = np.where(underlyingPrice > strike, underlyingPrice - strikePayoff, 0) if optionType == 1 else np.where(strike > underlyingPrice, strikePayoff - underlyingPrice, 0)
        return payoff.item() if isinstance(underlyingPrice, Real) else payoff

    def __init__(self, optionType: int, strike: Real, strikePayoff: Real) -> None:
        super(GapPayoff, self).__init__(GapPayoff.gapPayoff, optionType=optionType, strike=strike, strikePayoff=strikePayoff)
