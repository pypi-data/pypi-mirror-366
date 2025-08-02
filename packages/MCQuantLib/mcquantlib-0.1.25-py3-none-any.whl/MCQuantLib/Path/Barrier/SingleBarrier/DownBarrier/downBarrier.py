import numpy as np
from typing import Tuple, Union
from numbers import Real
from MCQuantLib.Path.Barrier.SingleBarrier.singleBarrier import Barrier, SingleBarrier

class DownBarrier(SingleBarrier):

    @staticmethod
    def downBarrierKnock(path: np.ndarray, barrier: Union[np.ndarray, Real], returnIndex: bool) -> np.ndarray:
        return DownBarrier.singleBarrierKnock(path=path, func=lambda p, b: p <= b, barrier=barrier, returnIndex=returnIndex)

    @staticmethod
    def downBarrierKnockAt(path: np.ndarray, barrier: Union[np.ndarray, Real], returnIndex: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return DownBarrier.singleBarrierKnockAt(path=path, func=lambda p, b: p <= b, barrier=barrier, returnIndex=returnIndex)

    def __init__(self, barrier: Union[np.ndarray, Real], returnIndex: bool = True, returnTime: bool = False) -> None:
        funcKnock = DownBarrier.downBarrierKnockAt if returnTime else DownBarrier.downBarrierKnock
        Barrier.__init__(self, funcKnock, barrier=barrier, returnIndex=returnIndex)

    def simple(self) -> 'Barrier':
        return self.switch(DownBarrier.downBarrierKnock)

    def detail(self) -> 'Barrier':
        return self.switch(DownBarrier.downBarrierKnockAt)
    
