import pandas as pd
from typing import Sequence, Optional, Callable
from numbers import Real
from MCQuantLib.Product.asian import Asian
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.AsianOption.AverageStrikeAsianOption.averageStrikeAsianOption import AverageStrikeAsianOption

class AverageStrike(Asian):

    def __init__(self, start: pd.Timestamp, observationDate: Sequence[pd.Timestamp], optionType: int, calendar: Calendar, avgFunc: Optional[Callable] = None) -> None:
        super(AverageStrike, self).__init__(start=start, observationDate=observationDate, calendar=calendar, avgFunc=avgFunc)
        self.optionType = optionType

    def toStructure(self, valuationDate: pd.Timestamp = None, spot: Real = None) -> InstrumentMC:
        tradingDayOffset = self.calendar.numTradingDaysBetween(self.start, valuationDate)
        observationDay = Asian.updateDayArray(self.observationDay, tradingDayOffset)
        return AverageStrikeAsianOption(spot=spot, observationDay=observationDay, optionType=self.optionType, avgFunc=self.avgFunc)
    
