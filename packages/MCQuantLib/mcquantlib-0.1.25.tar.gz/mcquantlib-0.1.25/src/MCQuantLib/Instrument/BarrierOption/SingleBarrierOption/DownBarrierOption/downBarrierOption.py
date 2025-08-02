import numpy as np
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Path.Barrier.SingleBarrier.DownBarrier.downBarrier import DownBarrier
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.singleBarrierOption import SingleBarrierOption
from MCQuantLib.Payoff.payoff import Payoff


class DownOutOption(SingleBarrierOption):
    """
    A down-and-out barrier option which is a discretely observed. It is
    knocked out if the price of the underlying asset is below the barrier level
    on close of any observation day. When the option is knocked out, a rebate is
    immediately paid to the option holder.
    """

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        knockTime, _, notKnockPath = DownBarrier.downBarrierKnockAt(logPath, self.logBarrier, returnIndex=False)
        terminal = notKnockPath[:, -1]
        surviving = self.payoff(np.exp(terminal)*self.spot) * discountFactor[-1]
        knockedOut = self.rebate[knockTime] * discountFactor[knockTime]
        pvTerminal = np.sum(surviving) if surviving.size > 0 else 0
        pvKnockedOut = np.sum(knockedOut) if knockedOut.size > 0 else 0
        return (pvTerminal + pvKnockedOut) / len(logPath)


class DownInOption(SingleBarrierOption):
    """
    A down-and-in option which is a discretely observed. It begins
    to function as a normal option once the price of the underlying
    asset is below the barrier level on close of any observation day.
    If during its life the barrier is never hit, a rebate will be paid
    to the option holder at maturity.
    """
    def __init__(self, spot: Real, barrier: Union[Sequence, Real], rebate: Real, observationDay: np.ndarray, payoff: Payoff) -> None:
        if hasattr(rebate, "__iter__"):
            raise ValueError("Rebates of knock-in options should be scalars")
        super(DownInOption, self).__init__(spot, barrier, rebate, observationDay, payoff, out=False)

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Real:
        knockPath = DownBarrier.downBarrierKnock(logPath, self.logBarrier, False)
        terminal = knockPath[:, -1]
        numberKnockIn = len(terminal)
        numVoided = len(logPath) - numberKnockIn
        payoffKnockIn = self.payoff(np.exp(terminal) * self.spot) * discountFactor[-1]
        pvKnockIn = np.sum(payoffKnockIn) if payoffKnockIn.size > 0 else 0
        return (pvKnockIn + self.rebate * numVoided * discountFactor[-1]) / len(logPath)

