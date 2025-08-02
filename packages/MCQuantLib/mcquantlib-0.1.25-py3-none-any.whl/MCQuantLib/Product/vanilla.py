import pandas as pd
from numbers import Real
from typing import Sequence
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.VanillaOption.vanillaOption import VanillaOption
from MCQuantLib.Product.product import Product
from MCQuantLib.Payoff.payoff import Payoff
from MCQuantLib.Tool.dateTool import Calendar


class Vanilla(Product):
    _structure = VanillaOption

    def __init__(self, start: pd.Timestamp, observationDate: Sequence[pd.Timestamp], payoff: Payoff, calendar: Calendar) -> None:
        self.calendar = Product.checkCalendar(calendar)
        self.start = Product.checkIsTrading(start, calendar)
        self.observationDate = observationDate
        self.payoff = Product.checkPayoff(payoff)
        self.observationDay = calendar.numTradingDaysBetweenGrid(start, observationDate)

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDay = Product.updateDayArray(self.observationDay, tradingDayOffset)
        return self.__class__._structure(spot=spot, observationDay=observationDay, payoff=self.payoff)

    def value(self, valuationDate: pd.Timestamp, spot: Real, *args, **kwargs):
        return self.toStructure(valuationDate, spot).calculateValue(*args, **kwargs)

