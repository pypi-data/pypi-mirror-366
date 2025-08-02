import pandas as pd
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.singleBarrierOption import SingleBarrierOption
from MCQuantLib.Product.product import Product
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Tool.arrayTool import Operation


class SingleBarrier(Product):
    _structure = SingleBarrierOption
    _out = True

    def __init__(self, start: pd.Timestamp, barrier: Union[Sequence, Real], rebate: Union[Sequence, Real], observationDate: Sequence[pd.Timestamp], payoff: Payoff, calendar: Calendar) -> None:
        self.calendar = Product.checkCalendar(calendar)
        self.start = Product.checkIsTrading(start, calendar)
        self.barrier = Operation.fromScalar(barrier, observationDate)

        if self.__class__._out:
            self.rebate = Operation.fromScalar(rebate, observationDate)
        else:
            if hasattr(rebate, "__iter__"):
                raise TypeError(
                    "rebate of knock-in options should be a scalar"
                )
            self.rebate = rebate

        self.observationDate = observationDate
        self.payoff = Product.checkPayoff(payoff)
        self.observationDay = calendar.numTradingDaysBetweenGrid(start, observationDate)

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDay, rebate, barrier = Product.updateDayArray(
            self.observationDay, tradingDayOffset, self.rebate, self.barrier
        )
        return self.__class__._structure(
            spot=spot, barrier=barrier, rebate=rebate,
            observationDay=observationDay, payoff=self.payoff
        )

    def value(self, valuationDate: pd.Timestamp, spot: Real, *args, **kwargs):
        return self.toStructure(valuationDate, spot).calculateValue(*args, **kwargs)

