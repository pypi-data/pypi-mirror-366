import numpy as np
from numbers import Real
from abc import ABC, abstractmethod


class Instrument(ABC):
    @abstractmethod
    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        pass

    @property
    @abstractmethod
    def spot(self) -> Real:
        pass

    @property
    @abstractmethod
    def simulatedTimeArray(self) -> np.ndarray:
        pass


class InstrumentMC(Instrument):

    def calculateValue(self, engine: 'Engine', process: 'Process', *args, **kwargs) -> Real:
        return engine.calculate(self, process, *args, **kwargs)

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        pass

    def _setSpot(self, value: Real) -> None:
        pass

    spot = property(lambda self: self._spot, _setSpot, lambda self: None)
    simulatedTimeArray = property(lambda self: self._simulatedTimeArray, lambda self, v: None, lambda self: None)

