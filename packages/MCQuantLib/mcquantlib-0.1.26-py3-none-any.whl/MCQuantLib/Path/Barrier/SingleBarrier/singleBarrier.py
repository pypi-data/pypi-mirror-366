import numpy as np
from typing import Tuple, Callable, Union
from numbers import Real
from MCQuantLib.Path.Barrier.barrier import Barrier

class SingleBarrier(Barrier):

    @staticmethod
    def singleBarrierKnock(path: np.ndarray, func: Callable[[np.ndarray, Union[np.ndarray, Real]], np.ndarray[bool]], barrier: Union[np.ndarray, Real], returnIndex: bool) -> np.ndarray:
        """
        Given a function that is used to judge whether path knocks at barrier,
        this function returns the index of those knocked-barrier path, or returns
        the path array of knocked-barrier path.

        Parameters
        -------------------
        path : Sequence
            An 2D array containing the paths to be evaluated.
        func : Callable[[np.ndarray, Union[np.ndarray, Real]]
            A function that returns a bool array. If this condition
            is satisfied and func returns True, then it means knock at
            the barrier.
        barrier : Union[np.ndarray, Real]
            Barrier level. It must match the length of
            each individual path.
        returnIndex : bool
            If True, return the indices of knock-outs and
            survivors, rather than the paths themselves.

        Returns
        --------------------
        knockIndex or knockPath
        """
        knockIndex = np.any(func(path, barrier), axis=1)
        return knockIndex if returnIndex else path[knockIndex]

    @staticmethod
    def singleBarrierKnockAt(path: np.ndarray, func: Callable[[np.ndarray, Union[np.ndarray, Real]], np.ndarray[bool]], barrier: Union[np.ndarray, Real], returnIndex: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Given a function that is used to judge whether path knocks at barrier,
        this function returns the index of those knocked-barrier path, or returns
        the path array of knocked-barrier path.

        Parameters
        -------------------
        path : Sequence
            An 2D array containing the paths to be evaluated.
        func : Callable[[np.ndarray, Union[np.ndarray, Real]]
            A function that returns a bool array. If this condition
            is satisfied and func returns True, then it means knock at
            the barrier.
        barrier : Union[np.ndarray, Real]
            Barrier level. It must match the length of
            each individual path.
        returnIndex : bool
            If True, return the indices of knock-outs and
            survivors, rather than the paths themselves.

        Returns
        --------------------
        knockTime, knockPath (or knockIndex), notKnockPath (or notKnockIndex)
        """
        knock = func(path, barrier)
        knockIndex = np.any(knock, axis=1)
        notKnockIndex = np.logical_not(knockIndex)
        knockTime = np.argmax(knock, axis=1).astype(int)
        return (knockTime, knockIndex, notKnockIndex) if returnIndex else (knockTime[knockIndex], path[knockIndex], path[notKnockIndex])

    def __init__(self, barrier: Union[np.ndarray, Real], func: Callable[[np.ndarray, Union[np.ndarray, Real]], np.ndarray[bool]], returnIndex: bool = True, returnTime: bool = False) -> None:
        funcKnock = SingleBarrier.singleBarrierKnockAt if returnTime else SingleBarrier.singleBarrierKnock
        Barrier.__init__(self, funcKnock, barrier=barrier, returnIndex=returnIndex, func=func)

    def simple(self) -> 'Barrier':
        """Just return index of knocked path."""
        return self.switch(SingleBarrier.singleBarrierKnock)
    
    def detail(self) -> 'Barrier':
        """Return a tuple of (knockTime, knockIndex, notKnockIndex)"""
        return self.switch(SingleBarrier.singleBarrierKnockAt)
