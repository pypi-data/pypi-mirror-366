import numpy as np
from numpy import log
from numbers import Real
from typing import Union, Sequence, Dict
from MCQuantLib.Tool.decoratorTool import FunctionParameterFreezer, ValueAsserter
from MCQuantLib.Tool.arrayTool import Operation
from MCQuantLib.Path.Barrier.SingleBarrier.UpBarrier.upBarrier import UpBarrier
from MCQuantLib.Path.Barrier.SingleBarrier.DownBarrier.downBarrier import DownBarrier
from MCQuantLib.Instrument.BarrierOption.barrierOption import BarrierOption
from MCQuantLib.Payoff.payoff import Payoff

class SingleBarrierCreator(object):

    @ValueAsserter(argIndexList=[5], argKeyList=['upOrDown'], value={'up', 'down'})
    def __init__(self, level: Union[Sequence, Real], rebate: Union[Sequence, Real], observationDay: np.ndarray, payoff: Payoff, upOrDown: str) -> None:
        self.level = Operation.fromScalar(level, observationDay)
        self.observationDay = observationDay
        self.payoff = payoff
        self.rebate = Operation.fromScalar(rebate, observationDay)
        self.upOrDown = upOrDown
        _freezer = FunctionParameterFreezer(barrier=self.level, returnIndex=False)
        self.helper = _freezer(UpBarrier.upBarrierKnockAt) if upOrDown == 'up' else _freezer(DownBarrier.downBarrierKnockAt)

    def filter(self, path: np.ndarray, discountFactor: np.ndarray) -> Dict:
        """Payoff of hitPath and path that do not hit the barrier."""
        terminalDiscountFactor = discountFactor[-1]
        hitTime, hitPath, notHitPath = self.helper(path)
        pvRebate = (self.rebate[hitTime] * discountFactor[hitTime]).sum() / len(path)
        pvPayoff = self.payoff(hitPath[:, -1]).sum() * terminalDiscountFactor / len(path)

        return {
            "PV": pvRebate + pvPayoff,
            "Hitting": hitPath,
            "Day first hit": hitTime,
            "Non-hitting": notHitPath
        }

    def fill(self, allObservationDay: np.ndarray, valueLevel: Union[np.ndarray, Real], valueRebate: Union[np.ndarray, Real] = 0) -> 'SingleBarrierCreator':
        level = Operation.fill(self.observationDay, allObservationDay, self.level, valueLevel)
        rebate = Operation.fill(self.observationDay, allObservationDay, self.rebate, valueRebate)
        obj = SingleBarrierCreator(level=level, observationDay=allObservationDay, upOrDown=self.upOrDown, rebate=rebate, payoff=self.payoff)
        return obj

    def toLog(self, spot: Real) -> 'SingleBarrierCreator':
        payoff = self.payoff.toLog(spot)
        obj = SingleBarrierCreator(level=log(self.level / spot), observationDay=self.observationDay, upOrDown=self.upOrDown, rebate=self.rebate, payoff=payoff)
        return obj

class SingleBarrierOption(BarrierOption):
    """Single-barrier options. Intended to be subclassed not used."""

    def __init__(self, spot: Real, barrier: Union[Sequence, Real], rebate: Union[Sequence, Real], observationDay: np.ndarray, payoff: Payoff, out: bool = True) -> None:
        self._spot = spot
        self.barrier = Operation.fromScalar(barrier, observationDay)
        self.rebate = Operation.fromScalar(rebate, observationDay) if out else rebate
        self.observationDay = observationDay
        self._simulatedTimeArray = np.append([0], observationDay)
        self.logBarrier = np.log(self.barrier / spot)
        self.payoff = payoff

    def _setSpot(self, value: Real) -> None:
        """Spot price should be larger than 0."""
        self._spot = value
        self.logBarrier = np.log(self.barrier / value)
