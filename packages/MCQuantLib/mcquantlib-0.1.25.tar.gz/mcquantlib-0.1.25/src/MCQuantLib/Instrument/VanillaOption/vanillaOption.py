import numpy as np
from numbers import Real
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Payoff.payoff import Payoff

class VanillaOption(InstrumentMC):
    def __init__(self, spot: Real, observationDay: np.ndarray, payoff: Payoff):
        self._spot = spot
        self.observationDay = observationDay
        self._simulatedTimeArray = np.append([0], observationDay)
        self.payoff = payoff

    def _setSpot(self, value: Real) -> None:
        """Spot price should be larger than 0."""
        self._spot = value

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        discountFactorTerminal = discountFactor[-1]
        payoffTerminal = self.payoff(np.exp(logPath[:, -1]) * self.spot)
        return np.sum(payoffTerminal * discountFactorTerminal) / len(logPath)

