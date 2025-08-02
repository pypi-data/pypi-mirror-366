import numpy as np
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import Payoff, PlainVanillaPayoff
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Path.Barrier.SingleBarrier.UpBarrier.upBarrier import UpBarrier
from MCQuantLib.Path.Barrier.SingleBarrier.DownBarrier.downBarrier import DownBarrier
from MCQuantLib.Tool.arrayTool import Operation


class AutoCallStructure(InstrumentMC):
    """
    This is the basic class of UpOut-DownIn Option. It is an abstract class which
    does not define payoff and pvLogPath.
    """
    def __init__(
            self, spot: Real, upperBarrierOut: Union[Sequence, Real], observationDayOut: np.ndarray,
            rebateOut: Union[Sequence, Real], lowerBarrierIn: Union[Sequence, Real], observationDayIn: np.ndarray
    ) -> None:
        """
        A structured products with a high barrier and a low barrier. The high barrier
        dominates the lower one in the sense that, when both a "knock-out" and a
        "knock-in" occur during the life of the product, the status is determined as
        "knock-out".

        Parameters
        -------------
        spot : Real
            The spot (i.e. on the valuation day) of the price of the underlying asset.
        upperBarrierOut : Real or Sequence
            The knock-out barrier level. Can be either a scalar
            or an array. If a scalar is passed, it will be treated as the time-invariant
            level of barrier. If an array is passed, it must match
            the length of *observationDayOut*.
        observationDayOut : Sequence
            A 1-D array of integers specifying observation days. Each of its elements
            represents the number of days that an observation day is from the valuation
            day.
        rebateOut : Real or Sequence
            The rebate of the option. If a constant is passed, then it will be
            treated as the *time-invariant* rebate paid to the option holder. If an array
            is passed, then it must match the length of *observationDayOut*.
        lowerBarrierIn : Real or Sequence
            Similar to *upperBarrierOut*.
        observationDayIn : Sequence
            Similar to *observationDayOut*.
        """
        self._spot = spot
        self.observationDayIn = observationDayIn
        self.observationDayOut = observationDayOut
        self.lowerBarrierIn = Operation.fromScalar(lowerBarrierIn, observationDayIn)
        self.upperBarrierOut = Operation.fromScalar(upperBarrierOut, observationDayOut)
        self.rebateOut = Operation.fromScalar(rebateOut, observationDayOut)
        self.logBarrierIn = np.log(self.lowerBarrierIn / spot)
        self.logBarrierOut = np.log(self.upperBarrierOut / spot)
        _t, self._indexIn, self._indexOut = Operation.merge(observationDayIn, observationDayOut)
        self._simulatedTimeArray = np.append([0], _t)

    def _setSpot(self, value: Real) -> None:
        """Spot price should be larger than 0."""
        self._spot = value
        self.logBarrierOut = np.log(self.upperBarrierOut / value)
        self.logBarrierIn = np.log(self.lowerBarrierIn / value)


class AutoCallOption(AutoCallStructure):
    """This is the basic class of Autocall option, it owns structure of UpOut - DownIn."""
    def __init__(
            self, spot: Real, upperBarrierOut: Union[Sequence, Real], observationDayOut: np.ndarray,
            rebateOut: Union[Sequence, Real], lowerBarrierIn: Union[Sequence, Real], observationDayIn: np.ndarray,
            payoffIn: Payoff, payoffNotKnock: Payoff
    ) -> None:
        """
        A structured products with a high barrier and a low barrier. The high barrier
        dominates the lower one in the sense that, when both a "knock-out" and a
        "knock-in" occur during the life of the product, the status is determined as
        "knock-out".

        Parameters
        ----------
        spot : Real
            The spot (i.e. on the valuation day) of the price of the underlying asset.
        upperBarrierOut : Real or Sequence
            The knock-out barrier level. Can be either a scalar
            or an array. If a scalar is passed, it will be treated as the time-invariant
            level of barrier. If an array is passed, it must match
            the length of *observationDayOut*.
        observationDayOut : Sequence
            A 1-D array of integers specifying observation days. Each of its elements
            represents the number of days that an observation day is from the valuation
            day.
        rebateOut : Real or Sequence
            The rebate of the option. If a constant is passed, then it will be
            treated as the *time-invariant* rebate paid to the option holder. If an array
            is passed, then it must match the length of *observationDayOut*.
        lowerBarrierIn : Real or Sequence
            Similar to *upperBarrierOut*.
        observationDayIn : Sequence
            Similar to *observationDayOut*.
        payoffIn : Payoff
            Applies when there is a "knock-in" but no "knock-out".
        payoffNotKnock : Payoff
            Applies when there is neither "knock-in" nor "knock-out".
        """
        super(AutoCallOption, self).__init__(spot, upperBarrierOut, observationDayOut, rebateOut, lowerBarrierIn,observationDayIn)
        self.payoffIn = payoffIn
        self.payoffNotKnock = payoffNotKnock

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        discountFactorKnockOutObservation = discountFactor[self._indexOut]
        discountFactorTerminal = discountFactor[-1]
        knockOutTimeIndex, knockOutIndex, notKnockOutIndex = UpBarrier.upBarrierKnockAt(path=logPath[:, self._indexOut], barrier=self.logBarrierOut, returnIndex=True)
        notKnockOutPath = logPath[notKnockOutIndex]
        knockInIndex = DownBarrier.downBarrierKnock(path=notKnockOutPath[:, self._indexIn], barrier=self.logBarrierIn, returnIndex=True)
        pathKnockIn = notKnockOutPath[knockInIndex]
        notKnockPath = notKnockOutPath[np.logical_not(knockInIndex)]
        pvOut = self.rebateOut[knockOutTimeIndex[knockOutIndex]] * discountFactorKnockOutObservation[knockOutTimeIndex[knockOutIndex]]
        pvIn = self.payoffIn(np.exp(pathKnockIn[:, -1]) * self.spot) * discountFactorTerminal
        pvNotKnock = self.payoffNotKnock(np.exp(notKnockPath[:, -1]) * self.spot) * discountFactorTerminal
        return (pvOut.sum() + pvIn.sum() + pvNotKnock.sum()) / len(logPath)
