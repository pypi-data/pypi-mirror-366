import numpy as np
from abc import ABC, abstractmethod
from numbers import Real
from typing import Dict, Type

class Process(ABC):
    def __init__(self) -> None:
        if not hasattr(self, 'dayCounter'):
            raise AttributeError("Attribute 'dayCounter' may be given in initialization.")

    @property
    @abstractmethod
    def coordinator(self) -> Type:
        pass

class ProcessMC(ABC):
    @abstractmethod
    def generateEps(self, seed: int, batchSize: int) -> np.ndarray:
        pass

    @abstractmethod
    def pathGivenEps(self, eps: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def shift(self, path: np.ndarray, ds: Real, dr: Real, dv: Real, eps: np.ndarray) -> Dict:
        pass
