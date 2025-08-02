import pandas as pd
from numbers import Real
from typing import Union, Sequence
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.BarrierOption.DoubleBarrierOption.doubleBarrierOption import DoubleBarrierOption, DoubleInOption, DoubleOutOption
from MCQuantLib.Product.product import Product
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Tool.arrayTool import Operation


class DoubleBarrier(Product):
    _structure = DoubleBarrierOption

    def __init__(self, start: pd.Timestamp, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], observationDateUp: Sequence[pd.Timestamp], observationDateDown: Sequence[pd.Timestamp], payoff: Payoff, calendar: Calendar) -> None:
        self.calendar = Product.checkCalendar(calendar)
        self.start = Product.checkIsTrading(start, calendar)
        self.barrierUp = Operation.fromScalar(barrierUp, observationDateUp)
        self.barrierDown = Operation.fromScalar(barrierDown, observationDateDown)
        self.observationDateUp = observationDateUp
        self.observationDateDown = observationDateDown
        self.payoff = Product.checkPayoff(payoff)
        self.observationDayUp = calendar.numTradingDaysBetweenGrid(start, observationDateUp)
        self.observationDayDown = calendar.numTradingDaysBetweenGrid(start, observationDateDown)

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        pass

    def value(self, valuationDate: pd.Timestamp, spot: Real, *args, **kwargs):
        return self.toStructure(valuationDate, spot).calculateValue(*args, **kwargs)

class DoubleOut(DoubleBarrier):
    _structure = DoubleOutOption

    def __init__(self, start: pd.Timestamp, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], rebateUp: Union[Sequence, Real], rebateDown: Union[Sequence, Real], observationDateUp: Sequence[pd.Timestamp], observationDateDown: Sequence[pd.Timestamp], payoff: Payoff, calendar: Calendar):
        super(DoubleOut, self).__init__(start, barrierUp, barrierDown, observationDateUp, observationDateDown, payoff, calendar)
        self.rebateUp = Operation.fromScalar(rebateUp, observationDateUp)
        self.rebateDown = Operation.fromScalar(rebateDown, observationDateDown)

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDayUp, rebateUp, barrierUp = Product.updateDayArray(
            self.observationDayUp, tradingDayOffset, self.rebateUp, self.barrierUp
        )
        observationDayDown, rebateDown, barrierDown = Product.updateDayArray(
            self.observationDayDown, tradingDayOffset, self.rebateDown, self.barrierDown
        )
        return self.__class__._structure(
            spot=spot, barrierUp=barrierUp, barrierDown=barrierDown, rebateUp=rebateUp, rebateDown=rebateDown,
            observationDayUp=observationDayUp, observationDayDown=observationDayDown, payoff=self.payoff
        )

class DoubleIn(DoubleBarrier):
    _structure = DoubleInOption

    def __init__(self, start: pd.Timestamp, barrierUp: Union[Sequence, Real], barrierDown: Union[Sequence, Real], rebate: Union[Sequence, Real], observationDateUp: Sequence[pd.Timestamp], observationDateDown: Sequence[pd.Timestamp], payoff: Payoff, calendar: Calendar):
        super(DoubleIn, self).__init__(start, barrierUp, barrierDown, observationDateUp, observationDateDown, payoff, calendar)
        if hasattr(rebate, "__iter__"):
            raise TypeError("rebate of knock-in options should be a scalar")
        self.rebate = rebate

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDayUp, barrierUp = Product.updateDayArray(self.observationDayUp, tradingDayOffset, self.barrierUp)
        observationDayDown, barrierDown = Product.updateDayArray(self.observationDayDown, tradingDayOffset, self.barrierDown)
        return self.__class__._structure(
            spot=spot, barrierUp=barrierUp, barrierDown=barrierDown,
            observationDayUp=observationDayUp, observationDayDown=observationDayDown, rebate=self.rebate, payoff=self.payoff
        )
