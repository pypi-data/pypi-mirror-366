import numpy as np
from numbers import Real
from typing import Callable, Optional
from MCQuantLib.Instrument.AsianOption.asianOption import AsianOption
from MCQuantLib.Tool.decoratorTool import ValueAsserter

class AverageStrikeAsianOption(AsianOption):
    @ValueAsserter(argIndexList=[3], argKeyList=['optionType'], value={1, -1})
    def __init__(self, spot: Real, observationDay: np.ndarray, optionType: int, avgFunc: Optional[Callable] = None):
        super(AverageStrikeAsianOption, self).__init__(spot, observationDay, avgFunc)
        self.optionType = optionType

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        discountFactorTerminal = discountFactor[-1]
        price = np.exp(logPath) * self.spot
        averagePrice = self.avgFunc(price)
        priceTerminal = price[:, -1]
        premium = (priceTerminal - averagePrice) * self.optionType
        payoffTerminal = np.where(premium > 0, premium, 0)
        return np.sum(payoffTerminal * discountFactorTerminal) / len(logPath)

