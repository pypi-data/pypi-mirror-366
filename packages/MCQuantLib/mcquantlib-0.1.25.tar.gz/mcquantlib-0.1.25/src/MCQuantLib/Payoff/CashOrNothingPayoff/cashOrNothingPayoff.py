import numpy as np
from numbers import Real
from typing import Union
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.decoratorTool import ValueAsserter

class CashOrNothingPayoff(Payoff):
    """
    For call option, if underlyingPrice > strike, return cashAmount, else return 0.
    For put option, if underlyingPrice < strike, return cashAmount, else return 0.
    """
    @staticmethod
    @ValueAsserter(argIndexList=[1], argKeyList=['optionType'], value={1, -1})
    def cashOrNothingPayoff(underlyingPrice: Union[np.ndarray, Real], optionType: int, strike: Real, cashAmount: Real) -> Union[np.ndarray, Real]:
        payoff = np.where(underlyingPrice > strike, cashAmount, 0) if optionType == 1 else np.where(strike > underlyingPrice, cashAmount, 0)
        return payoff.item() if isinstance(underlyingPrice, Real) else payoff

    def __init__(self, optionType: int, strike: Real, cashAmount: Real) -> None:
        super(CashOrNothingPayoff, self).__init__(CashOrNothingPayoff.cashOrNothingPayoff, optionType=optionType, strike=strike, cashAmount=cashAmount)
