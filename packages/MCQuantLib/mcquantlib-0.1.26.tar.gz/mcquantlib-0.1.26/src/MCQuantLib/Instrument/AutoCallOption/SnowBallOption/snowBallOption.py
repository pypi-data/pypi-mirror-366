import numpy as np
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff
from MCQuantLib.Instrument.AutoCallOption.autocallOption import AutoCallStructure
from MCQuantLib.Path.Barrier.SingleBarrier.UpBarrier.upBarrier import UpBarrier
from MCQuantLib.Path.Barrier.SingleBarrier.DownBarrier.downBarrier import DownBarrier


class SnowBallOption(AutoCallStructure):
    def __init__(self, spot: Real, upperBarrierOut: Union[Sequence, Real], lowerBarrierIn: Union[Sequence, Real], observationDayIn: np.ndarray, observationDayOut: np.ndarray, rebateOut: np.ndarray, fullCoupon: Real) -> None:
        """
        A snowball gives its holder a large payoff if
        the price of the underlying asset stays between a certain range.
        If the price of the underlying asset exceeds the knock-out barrier
        on any observation day, the contract ends immediately and coupon
        is paid to the holder with the amount depending on the day of knock-out.
        Major reason for large loss to the holder could be a plummet in the
        price of the underlying asset.

        Parameters
        ----------
        spot : Real
            The spot (i.e. on the valuation day) of the price of the underlying asset.
        upperBarrierOut : Real or Sequence
            The knock-out barrier level. Can be either a scalar
            or an array. If a scalar is passed, it will be treated as the time-invariant
            level of barrier. If an array is passed, it must match
            the length of *observationDayOut*.
        lowerBarrierIn : Real or Sequence
            The knock-in barrier level. Similar to *barrier-out*.
        observationDayIn : Sequence
            The observation day for knock-in. Must be an array of
            integers with each of its elements indicating the number of days that
            an observation day is away from the valuation day.
        observationDayOut : Sequence
            The observation day for knock-out. Similar to *observationDayIn*.
        rebateOut : Sequence
            Coupon paid to the holder in a knock-out event.
            Must match the length of *observationDayOut*. Note that this should be specified
            in absolute amounts, not in percentages.
        fullCoupon : Real
            Coupon paid to the holder if the contract survives to maturity day without
            knock-out or knock-in. Note that this should be specified in absolute
            amounts, not in percentages.
        """
        super(SnowBallOption, self).__init__(spot, upperBarrierOut, observationDayOut, rebateOut, lowerBarrierIn, observationDayIn)
        self.fullCoupon = fullCoupon
        self._strike = spot

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        discountFactorKnockOutObservation = discountFactor[self._indexOut]
        _discountFactor = discountFactor[-1]
        knockOutTimeIndex, knockOutIndex, notKnockOutIndex = UpBarrier.upBarrierKnockAt(logPath[:, self._indexOut], self.logBarrierOut, returnIndex=True)
        pvOut = self.rebateOut[knockOutTimeIndex[knockOutIndex]] * discountFactorKnockOutObservation[knockOutTimeIndex[knockOutIndex]]
        pathNotKnockOut = logPath[notKnockOutIndex]
        pathKnockIn = DownBarrier.downBarrierKnock(pathNotKnockOut[:, self._indexIn], self.logBarrierIn, returnIndex=False)
        pvIn = -PlainVanillaPayoff.plainVanillaPayoff(np.exp(pathKnockIn[:, -1])*self.spot, strike=self._strike, optionType=-1) * _discountFactor
        pvFullCoupon = (len(logPath) - len(pvOut) - len(pvIn)) * self.fullCoupon * _discountFactor
        return (pvOut.sum() + pvIn.sum() + pvFullCoupon) / len(logPath)
