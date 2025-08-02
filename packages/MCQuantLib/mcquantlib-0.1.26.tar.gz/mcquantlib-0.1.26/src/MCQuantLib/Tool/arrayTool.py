import numpy as np
from numbers import Real
from typing import Tuple, Union, Sequence

class Operation(object):

    @staticmethod
    def merge(arrayLeft: np.ndarray, arrayRight: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Given two arrays, return the union of them and
        the where they are in the new array.
        """
        merged = np.sort(np.unique(np.concatenate([arrayLeft, arrayRight])))
        arrayLeftIndex = np.isin(merged, arrayLeft)
        arrayRightIndex = np.isin(merged, arrayRight)
        return merged, arrayLeftIndex, arrayRightIndex

    @staticmethod
    def fromScalar(value: Union[Sequence, Real], like: Sequence) -> np.ndarray:
        """
        Convert a scalar to an array that matches the length of given array.
        If value is already an array, it must have the same length with given array.
        """
        return np.array(value) if hasattr(value, "__iter__") and len(value) != len(like) else np.full(len(like), value)

    @staticmethod
    def fill(subset: np.ndarray, allset: np.ndarray, valueSubset: Union[np.ndarray, Real], valueAllset: Union[np.ndarray, Real]) -> np.ndarray:
        """
        If the element in allset is also in subset, then use valueSubset, if not, use valueAllset.
        Return the array whose length is the same as allset, and elements are either valueSubset or valueAllset.
        """
        inSubset = np.isin(allset, subset)
        if np.isscalar(valueSubset):
            return np.where(inSubset, valueSubset, valueAllset)
        else:
            filled = np.full(len(allset), valueAllset)
            filled[inSubset] = valueSubset
            return filled
