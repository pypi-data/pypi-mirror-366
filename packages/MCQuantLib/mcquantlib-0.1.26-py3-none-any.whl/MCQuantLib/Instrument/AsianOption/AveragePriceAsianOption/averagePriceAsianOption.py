import numpy as np
from numbers import Real
from typing import Callable, Optional
from MCQuantLib.Instrument.AsianOption.asianOption import AsianOption
from MCQuantLib.Tool.decoratorTool import ValueAsserter

class AveragePriceAsianOption(AsianOption):
    @ValueAsserter(argIndexList=[3], argKeyList=['optionType'], value={1, -1})
    def __init__(self, spot: Real, observationDay: np.ndarray, optionType: int, strike: Real, avgFunc: Optional[Callable] = None):
        super(AveragePriceAsianOption, self).__init__(spot, observationDay, avgFunc)
        self.optionType = optionType
        self.strike = strike

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        discountFactorTerminal = discountFactor[-1]
        price = np.exp(logPath) * self.spot
        averagePrice = self.avgFunc(price)
        premium = (averagePrice - self.strike) * self.optionType
        payoffTerminal = np.where(premium > 0, premium, 0)
        return np.sum(payoffTerminal * discountFactorTerminal) / len(logPath)

