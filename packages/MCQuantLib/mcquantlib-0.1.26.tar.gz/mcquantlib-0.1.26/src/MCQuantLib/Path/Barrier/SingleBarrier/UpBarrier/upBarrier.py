import numpy as np
from typing import Tuple, Union
from numbers import Real
from MCQuantLib.Path.Barrier.SingleBarrier.singleBarrier import Barrier, SingleBarrier

class UpBarrier(SingleBarrier):

    @staticmethod
    def upBarrierKnock(path: np.ndarray, barrier: Union[np.ndarray, Real], returnIndex: bool) -> np.ndarray:
        return UpBarrier.singleBarrierKnock(path=path, func=lambda p, b: p >= b, barrier=barrier, returnIndex=returnIndex)

    @staticmethod
    def upBarrierKnockAt(path: np.ndarray, barrier: Union[np.ndarray, Real], returnIndex: bool) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray]:
        return UpBarrier.singleBarrierKnockAt(path=path, func=lambda p, b: p >= b, barrier=barrier, returnIndex=returnIndex)

    def __init__(self, barrier: Union[np.ndarray, Real], returnIndex: bool = True, returnTime: bool = False) -> None:
        funcKnock = UpBarrier.upBarrierKnockAt if returnTime else UpBarrier.upBarrierKnock
        Barrier.__init__(self, funcKnock, barrier=barrier, returnIndex=returnIndex)

    def simple(self) -> 'Barrier':
        return self.switch(UpBarrier.upBarrierKnock)

    def detail(self) -> 'Barrier':
        return self.switch(UpBarrier.upBarrierKnockAt)

