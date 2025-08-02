import numpy as np
from numbers import Real
from typing import Union, Sequence, Optional
from MCQuantLib.Path.Barrier.DoubleBarrier.doubleBarrier import DoubleBarrier
from MCQuantLib.Instrument.BarrierOption.barrierOption import BarrierOption
from MCQuantLib.Tool.arrayTool import Operation
from MCQuantLib.Payoff.payoff import Payoff


class DoubleBarrierOption(BarrierOption):
    """Double-barrier options. It is an abstract class and may not be used directly."""

    def __init__(self, spot: Real, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], observationDayUp: np.ndarray, observationDayDown: np.ndarray, payoff: Payoff) -> None:
        self._spot = spot
        self.barrierUp = Operation.fromScalar(barrierUp, observationDayUp)
        self.barrierDown = Operation.fromScalar(barrierDown, observationDayDown)
        self.observationDayUp = observationDayUp
        self.observationDayDown = observationDayDown

        self.logBarrierUp = np.log(self.barrierUp / spot)
        self.logBarrierDown = np.log(self.barrierDown / spot)

        self._t, _, _ = Operation.merge(observationDayUp, observationDayDown)
        self._filledUp = Operation.fill(observationDayUp, self._t, self.logBarrierUp, np.inf)
        self._filledDown = Operation.fill(observationDayDown, self._t, self.logBarrierDown, -np.inf)
        self._simulatedTimeArray = np.append([0], self._t)
        self.payoff = payoff

    def _setSpot(self, value: Real) -> None:
        """Spot price should be larger than 0."""
        self._spot = value
        self.logBarrierUp = np.log(self.barrierUp / value)
        self.logBarrierDown = np.log(self.barrierDown / value)
        self._filledUp = Operation.fill(self.observationDayUp, self._t, self.logBarrierUp, np.inf)
        self._filledDown = Operation.fill(self.observationDayDown, self._t, self.logBarrierDown, -np.inf)


class DoubleOutOption(DoubleBarrierOption):
    def __init__(self, spot: Real, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], observationDayUp: np.ndarray, observationDayDown: np.ndarray, payoff: Payoff, rebate: Optional[Union[Sequence, Real]] = None, rebateUp: Optional[Union[Sequence, Real]] = None, rebateDown: Optional[Union[Sequence, Real]] = None) -> None:
        """ 
        A double-out option which is discretely observed. It is knocked out if
        the price of the underlying asset is above the upper barrier or below the lower barrier.
        A rebate is paid to the option holder once the option is knocked out.
    
        Parameters
        ----------
        spot : Real 
            The spot price of the underlying asset.
        barrierUp : Real or Sequence 
            The upper barrier of the option. This can be either
            a scalar or an array. If a scalar is passed, it will be treated as
            the time-invariant level of barrier. If an array is passed, it must
            match the length of *observationDayUp*.
        barrierDown : Real or Sequence
            The lower barrier of the option. This can be either
            a scalar or an array. If a scalar is passed, it will be treated as
            the time-invariant level of barrier. If an array is passed, it must
            match the length of *observationDayDown*.
        observationDayUp : Sequence
            The array of observation days for the upper barrier.
            This must be an array of integers with each element representing
            the number of days that an observation day is from the valuation day.
            The last element of the union of *observationDayUp* and *observationDayDown* is
            assumed to be the maturity of the double-barrier option.
        observationDayDown:
            Similar to *observationDayUp*.
        payoff : Payoff
            The object of Payoff class.
        rebate : Real or Sequence
            If a scalar or an array is passed, then identical rebates will
            apply to knock-outs from above and below. If *rebate* is specified, both
            *rebateUp* and *rebateDown* will be ignored. If an array is passed,
            it must match the length of the union of *observationDayUp* and *observationDayDown*
        rebateUp : Real or Sequence
            The rebate paid to the holder if the option is knocked
            out from above. Can be either a scalar or an array.
        rebateDown : Real or Sequence
            The rebate paid to the holder if the option is knocked
            out from below. Can be either a scalar or an array.
        """
        super(DoubleOutOption, self).__init__(spot, barrierUp, barrierDown, observationDayUp, observationDayDown, payoff)
        if rebate is None:
            if (rebateUp is None) or (rebateDown is None):
                raise AttributeError("Both rebateUp and rebateDown must be specified when rebate is None")
            self.rebateUp = Operation.fromScalar(rebateUp, observationDayUp)
            self.rebateDown = Operation.fromScalar(rebateDown, observationDayDown)
            self._filledRebateUp = Operation.fill(observationDayUp, self._t, self.rebateUp, np.nan)
            self._filledRebateDown = Operation.fill(observationDayDown, self._t, self.rebateDown, np.nan)
            self._identicalRebate = False
        else:
            self.rebate = Operation.fromScalar(rebate, self._t)
            self._identicalRebate = True

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        if self._identicalRebate:
            knockTime, _, notKnockPath = DoubleBarrier.doubleBarrierKnockAt(logPath, self._filledUp, self._filledDown, False)
            knockedOut = self.rebate[knockTime] * discountFactor[knockTime]
            pvKnockedOut = knockedOut.sum()

        else:
            knockTime, knockPath, notKnockPath = DoubleBarrier.doubleBarrierKnockAt(logPath, self._filledUp, self._filledDown, False)
            knockPrice = knockPath[range(len(knockPath)), knockTime]
            upBarrierWhenKnocked = self._filledUp[knockTime]
            downBarrierWhenKnocked = self._filledDown[knockTime]
            upKnockTime = knockTime[knockPrice >= upBarrierWhenKnocked]
            downKnockTime = knockTime[knockPrice <= downBarrierWhenKnocked]

            pvKnockedOut = (
                (self._filledRebateUp[upKnockTime] * discountFactor[upKnockTime]).sum() +
                (self._filledRebateDown[downKnockTime] * discountFactor[downKnockTime]).sum()
            )

        surviving = self.payoff(np.exp(notKnockPath[:, -1]) * self.spot) * discountFactor[-1]
        pvTerminal = np.sum(surviving)

        return (pvTerminal + pvKnockedOut) / len(logPath)


class DoubleInOption(DoubleBarrierOption):
    def __init__(self, spot: Real, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], observationDayUp: np.ndarray, observationDayDown: np.ndarray, rebate: Real, payoff: Payoff) -> None:
        """ 
        A double-in option which is discretely observed. It begins to function
        as a normal function (i.e., knocks in) if on close of any observation
        day the price of the underlying asset is above the upper barrier or the
        lower barrier. A rebate is paid at the maturity if the option does not
        knock in during its life.

        Parameters
        ----------
        spot : Real
            The spot price of the underlying asset.
        barrierUp : Real or Sequence
            The upper barrier of the option. This can be either
            a scalar or an array. If a scalar is passed, it will be treated as
            the time-invariant level of barrier. If an array is passed, it must
            match the length of *observationDayUp*.
        barrierDown : Real or Sequence
            The lower barrier of the option. This can be either
            a scalar or an array. If a scalar is passed, it will be treated as
            the time-invariant level of barrier. If an array is passed, it must
            match the length of *observationDayDown*.
        observationDayUp : Sequence
            The array of observation days for the upper barrier.
            This must be an array of integers with each element representing
            the number of days that an observation day is from the valuation day.
            The last element of the union of *observationDayUp* and *observationDayDown* is
            assumed to be the maturity of the double-barrier option.
        observationDayDown : Sequence 
            Similar to *observationDayUp*.
        rebate : Real
            The rebate of the option. Must be a constant for knock-in options
        payoff : Payoff
            An object of Payoff class.
        """
        if hasattr(rebate, "__iter__"):
            raise ValueError("Rebates of knock-in options should be a scalar")
        super(DoubleInOption, self).__init__(spot, barrierUp, barrierDown, observationDayUp, observationDayDown, payoff)
        self.rebate = rebate

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        knockPath = DoubleBarrier.doubleBarrierKnock(logPath, self._filledUp, self._filledDown, False)
        terminal = knockPath[:, -1]
        numberKnockIn = len(terminal)
        numVoided = len(logPath) - numberKnockIn
        payoffKnockIn = self.payoff(np.exp(terminal) * self.spot) * discountFactor[-1]
        pvKnockIn = np.sum(payoffKnockIn) if payoffKnockIn.size > 0 else 0
        return (pvKnockIn + self.rebate * numVoided * discountFactor[-1]) / len(logPath)
