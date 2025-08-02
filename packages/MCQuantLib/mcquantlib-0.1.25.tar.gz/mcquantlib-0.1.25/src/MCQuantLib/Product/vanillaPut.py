import pandas as pd
from numbers import Real
from typing import Sequence
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.VanillaOption.VanillaPutOption.vanillaPutOption import VanillaPutOption
from MCQuantLib.Product.vanilla import Vanilla
from MCQuantLib.Tool.dateTool import Calendar


class VanillaPut(Vanilla):
    _structure = VanillaPutOption

    def __init__(self, start: pd.Timestamp, observationDate: Sequence[pd.Timestamp], strike: Real, calendar: Calendar) -> None:
        self.calendar = Vanilla.checkCalendar(calendar)
        self.start = Vanilla.checkIsTrading(start, calendar)
        self.observationDate = observationDate
        self.strike = strike
        self.observationDay = calendar.numTradingDaysBetweenGrid(start, observationDate)

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDay = Vanilla.updateDayArray(self.observationDay, tradingDayOffset)
        return self.__class__._structure(spot=spot, observationDay=observationDay, strike=self.strike)

