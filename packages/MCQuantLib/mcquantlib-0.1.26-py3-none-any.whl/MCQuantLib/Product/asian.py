import pandas as pd
from typing import Sequence, Optional, Callable
from numbers import Real
from MCQuantLib.Product.product import Product
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.AsianOption.asianOption import AsianOption

class Asian(Product):

    def __init__(self, start: pd.Timestamp, observationDate: Sequence[pd.Timestamp], calendar: Calendar, avgFunc: Optional[Callable] = None) -> None:
        self.calendar = Product.checkCalendar(calendar)
        self.start = Product.checkIsTrading(start, calendar)
        self.observationDate = observationDate
        self.observationDay = calendar.numTradingDaysBetweenGrid(start, observationDate)
        self.avgFunc = avgFunc

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDay = Product.updateDayArray(self.observationDay, tradingDayOffset)
        return AsianOption(spot=spot, observationDay=observationDay, avgFunc=self.avgFunc)

    def value(self, valuationDate: pd.Timestamp, spot: Real, *args, **kwargs):
        return self.toStructure(valuationDate, spot).calculateValue(*args, **kwargs)

