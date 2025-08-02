import numpy as np
from numbers import Real
from typing import Union
from MCQuantLib.Payoff.payoff import Payoff

class ConstantPayoff(Payoff):
    """Return amount no matter what option type or underlyingPrice."""
    @staticmethod
    def constantPayoff(underlyingPrice: Union[np.ndarray, Real], amount: Real) -> Union[np.ndarray, Real]:
        return amount if isinstance(underlyingPrice, Real) else np.full(len(underlyingPrice), amount)

    def __init__(self, amount: Real) -> None:
        super(ConstantPayoff, self).__init__(ConstantPayoff.constantPayoff, amount=amount)
