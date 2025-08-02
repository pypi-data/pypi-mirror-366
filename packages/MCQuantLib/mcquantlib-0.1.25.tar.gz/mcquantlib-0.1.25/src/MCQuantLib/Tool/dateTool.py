import pandas as pd
import QuantLib as ql
from typing import List, Optional, Sequence
from MCQuantLib.Tool.decoratorTool import StringTimestampConverter

class Calendar(object):
    unitKey = ['W', 'w', 'M', 'm', 'D', 'd', 'Y', 'y']
    unitValue = [ql.Weeks, ql.Weeks, ql.Months, ql.Months, ql.Days, ql.Days, ql.Years, ql.Years]
    unitMap = dict(zip(unitKey, unitValue))

    @staticmethod
    def parsePeriod(period: str) -> (int, int):
        n, unit = int(period[:-1]), period[-1]
        assert n > 0
        assert unit in set(Calendar.unitKey)
        return n, Calendar.unitMap[unit]

    @staticmethod
    def timestampToDate(date: pd.Timestamp) -> ql.Date:
        return ql.Date(date.day, date.month, date.year)

    @staticmethod
    def dateToTimestamp(date: ql.Date) -> pd.Timestamp:
        return pd.Timestamp(date.to_date())

    @StringTimestampConverter(argIterableIndexList=[2], argIterableKeyList=['otherHolidays'])
    def __init__(self, holidayRule: ql.Calendar, otherHolidays: Optional[Sequence[pd.Timestamp]] = None) -> None:
        self.updateCalendar(holidayRule, otherHolidays)

    @StringTimestampConverter(argIterableIndexList=[2], argIterableKeyList=['otherHolidays'])
    def updateCalendar(self, holidayRule: ql.Calendar, otherHolidays: Optional[Sequence[pd.Timestamp]] = None) -> None:
        """Create a custom calendar using QuantLib."""
        otherHolidays = otherHolidays if otherHolidays else []
        self.addHolidayRule(holidayRule)
        self.addHolidays(otherHolidays)

    def addHolidayRule(self, holidayRule: ql.Calendar) -> None:
        """Add customized holiday rule, this will overwrite current holiday settings."""
        self._otherHolidays = []
        self._qlCalendar = holidayRule
        self._holidayRule = self._qlCalendar.isHoliday

    @StringTimestampConverter(argIterableIndexList=[1], argIterableKeyList=['holidays'])
    def addHolidays(self, holidays: Sequence[pd.Timestamp]) -> None:
        """Add customized holiday."""
        self._otherHolidays.extend(holidays)
        [self._qlCalendar.addHoliday(Calendar.timestampToDate(i)) for i in holidays]
        self._holidayRule = self._qlCalendar.isHoliday

    @StringTimestampConverter(argIndexList=[1],argKeyList=['date'])
    def isTrading(self, date: pd.Timestamp) -> bool:
        """Return True if a day is trading day."""
        return not self._holidayRule(Calendar.timestampToDate(date))

    @StringTimestampConverter(argIndexList=[1,2], argKeyList=['start', 'end'])
    def tradingDaysBetween(self, start: pd.Timestamp, end: pd.Timestamp, startPoint: bool = True, endPoint: bool = True) -> List[pd.Timestamp]:
        """
        Return a list of trading days between *start* and *end*. Endpoints
        are counted only if they are trading.
        """
        startAdjust = start if startPoint else start + pd.Timedelta(days=1)
        startQlDate = Calendar.timestampToDate(startAdjust)
        endAdjust = end if endPoint else end + pd.Timedelta(days=-1)
        endQlDate = Calendar.timestampToDate(endAdjust)
        return [Calendar.dateToTimestamp(i) for i in self._qlCalendar.businessDayList(startQlDate, endQlDate)]

    @StringTimestampConverter(argIndexList=[1], argKeyList=['date'])
    def offset(self, date: pd.Timestamp, n: int, period: int = ql.Days) -> pd.Timestamp:
        """Return date of trading day *n* days before or after *date*."""
        qlDate = Calendar.timestampToDate(date)
        offsetDate = self._qlCalendar.advance(qlDate, n, period)
        return Calendar.dateToTimestamp(offsetDate)

    @StringTimestampConverter(argIndexList=[1, 2], argKeyList=['start', 'end'])
    def makeSchedule(self, start: pd.Timestamp, end: pd.Timestamp, period: str, forwardAdjust: bool = True, forwardScale: bool = True, forwardAdjustEndDay: bool = False):
        """Generate periodical trading dates between start and end, given period."""
        n, periodQl = Calendar.parsePeriod(period)
        convention = ql.Following if forwardAdjust else ql.Preceding
        terminalDateConvention = ql.Following if forwardAdjustEndDay else ql.Preceding
        forwards, backwards = (True, False) if forwardScale else (False, True)
        startQlDate, endQlDate = Calendar.timestampToDate(start), Calendar.timestampToDate(end)
        schedule = ql.MakeSchedule(startQlDate, endQlDate, ql.Period(n, periodQl), calendar=self._qlCalendar, convention=convention, terminalDateConvention=terminalDateConvention,forwards=forwards, backwards=backwards)
        return [Calendar.dateToTimestamp(i) for i in schedule]

    @StringTimestampConverter(argIndexList=[1], argKeyList=['start'])
    def makeScheduleByPeriod(self, start: pd.Timestamp, period: str, count: int, forwardAdjust: bool = True) -> List[pd.Timestamp]:
        """Generate periodical trading dates."""
        n, periodQl = Calendar.parsePeriod(period)
        convention = ql.Following if forwardAdjust else ql.Preceding
        dateQl = Calendar.timestampToDate(start)
        tradingDates = [self._qlCalendar.advance(dateQl, i*n, periodQl, convention) for i in range(count)]
        return [Calendar.dateToTimestamp(i) for i in tradingDates]

    @StringTimestampConverter(argIndexList=[1, 2], argKeyList=['start', 'end'])
    def numTradingDaysBetween(self, start: pd.Timestamp, end: pd.Timestamp, countStart: bool = False, countEnd: bool = True) -> int:
        """Return number of trading days between two dates."""
        startQlDate, endQlDate = Calendar.timestampToDate(start), Calendar.timestampToDate(end)
        return self._qlCalendar.businessDaysBetween(startQlDate, endQlDate, countStart, countEnd)

    @StringTimestampConverter(argIndexList=[1], argKeyList=['start'], argIterableIndexList=[2], argIterableKeyList=['dateList'])
    def numTradingDaysBetweenGrid(self, start: pd.Timestamp, dateList: Sequence[pd.Timestamp], countStart: bool = False, countEnd: bool = True) -> List[int]:
        """Return number of trading days between a date and a date list."""
        return [self.numTradingDaysBetween(start, end, countStart, countEnd) for end in dateList]
