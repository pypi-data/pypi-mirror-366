import numpy as np
from numbers import Real
from typing import Callable, Optional
from MCQuantLib.Instrument.instrument import InstrumentMC


class AsianOption(InstrumentMC):
    def __init__(self, spot: Real, observationDay: np.ndarray, avgFunc: Optional[Callable] = None):
        self._spot = spot
        self.observationDay = observationDay
        self._simulatedTimeArray = np.append([0], observationDay)
        self.avgFunc = avgFunc if avgFunc else (lambda x: np.mean(x, axis=1))
