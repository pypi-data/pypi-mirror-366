import numpy as np
from typing import Tuple, Union
from numbers import Real
from MCQuantLib.Path.Barrier.barrier import Barrier
from MCQuantLib.Path.Barrier.SingleBarrier.UpBarrier.upBarrier import UpBarrier
from MCQuantLib.Path.Barrier.SingleBarrier.DownBarrier.downBarrier import DownBarrier

class DoubleBarrier(UpBarrier, DownBarrier):

    @staticmethod
    def doubleBarrierKnock(path: np.ndarray, barrierUp: Union[np.ndarray, Real], barrierDown: Union[np.ndarray, Real], returnIndex: bool) -> np.ndarray:
        """
        Returns the third element of function doubleKnockTimeAndSurvivingPath
        but with a higher speed.
        """
        knockUp = UpBarrier.upBarrierKnock(path, barrierUp, True)
        knockDown = DownBarrier.downBarrierKnock(path, barrierDown, True)
        knockIndex = knockUp | knockDown
        return knockIndex if returnIndex else path[knockIndex]

    @staticmethod
    def doubleBarrierKnockAt(path: np.ndarray, barrierUp: Union[np.ndarray, Real], barrierDown: Union[np.ndarray, Real], returnIndex: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        upKnockTime, upKnockIndex, upNotKnockIndex = UpBarrier.upBarrierKnockAt(path, barrierUp, True)
        downKnockTime, downKnockIndex, downNotKnockIndex = DownBarrier.downBarrierKnockAt(path, barrierDown, True)
        knockIndex = upKnockIndex | downKnockIndex
        notKnockIndex = np.logical_not(knockIndex)
        condition = [upKnockIndex & downNotKnockIndex, upNotKnockIndex & downKnockIndex, upNotKnockIndex & downNotKnockIndex, upKnockIndex & downKnockIndex]
        choice = [upKnockTime, downKnockTime, np.zeros(len(path), dtype=int), np.min([upKnockTime, downKnockTime], axis=0)]
        knockTime = np.select(condition, choice)
        return (knockTime, knockIndex, notKnockIndex) if returnIndex else (knockTime[knockIndex], path[knockIndex], path[notKnockIndex])

    def __init__(self, barrierUp: Real, barrierDown: Real, returnIndex: bool = True, returnTime: bool = False) -> None:
        funcKnock = DoubleBarrier.doubleBarrierKnockAt if returnTime else DoubleBarrier.doubleBarrierKnock
        Barrier.__init__(self, funcKnock, barrierUp = barrierUp, barrierDown = barrierDown, returnIndex = returnIndex)
    
    def simple(self) -> 'Barrier':
        return self.switch(DoubleBarrier.doubleBarrierKnock)

    def detail(self) -> 'Barrier':
        return self.switch(DoubleBarrier.doubleBarrierKnockAt)

