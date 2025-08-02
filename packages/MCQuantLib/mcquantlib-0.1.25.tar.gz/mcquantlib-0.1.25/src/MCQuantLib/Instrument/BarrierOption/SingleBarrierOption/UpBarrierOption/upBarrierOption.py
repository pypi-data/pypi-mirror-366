import numpy as np
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Path.Barrier.SingleBarrier.UpBarrier.upBarrier import UpBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.singleBarrierOption import SingleBarrierOption
from MCQuantLib.Payoff.payoff import Payoff


class UpOutOption(SingleBarrierOption):
    """
    An up-and-out option which is a discretely observed. It
    is knocked out if the price of the underlying asset is larger
    than the barrier level on close of any observation day.
    When the option is knocked out, a rebate is immediately paid to the
    option holder.
    """

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        knockTime, _, notKnockPath = UpBarrier.upBarrierKnockAt(logPath, self.logBarrier, returnIndex=False)
        terminal = notKnockPath[:, -1]
        surviving = self.payoff(np.exp(terminal)*self.spot) * discountFactor[-1]
        knockedOut = self.rebate[knockTime] * discountFactor[knockTime]
        pvTerminal = np.sum(surviving) if surviving.size > 0 else 0
        pvKnockedOut = np.sum(knockedOut) if knockedOut.size > 0 else 0
        return (pvTerminal + pvKnockedOut) / len(logPath)


class UpInOption(SingleBarrierOption):
    """
    An up-and-in option which is a discretely observed. It begins to function
    as a normal option once the price of the underlying asset is above the barrier level
    on close of any observation day. If the barrier is never
    hit during its life, a rebate will be paid to the option holder at maturity.
    """
    def __init__(self, spot: Real, barrier: Union[Sequence, Real], rebate: Real, observationDay: np.ndarray, payoff: Payoff) -> None:
        if hasattr(rebate, "__iter__"):
            raise ValueError("Rebates of knock-in options should be scalars")
        super(UpInOption, self).__init__(spot, barrier, rebate, observationDay, payoff, out=False)

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        knockPath = UpBarrier.upBarrierKnock(logPath, self.logBarrier, False)
        terminal = knockPath[:, -1]
        numberKnockIn = len(terminal)
        numVoided = len(logPath) - numberKnockIn
        payoffKnockIn = self.payoff(np.exp(terminal) * self.spot) * discountFactor[-1]
        pvKnockIn = np.sum(payoffKnockIn) if payoffKnockIn.size > 0 else 0
        return (pvKnockIn + self.rebate * numVoided * discountFactor[-1]) / len(logPath)

