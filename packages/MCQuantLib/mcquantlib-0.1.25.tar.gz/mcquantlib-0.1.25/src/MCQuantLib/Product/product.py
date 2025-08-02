import pandas as pd
from numbers import Real
from typing import Sequence, Tuple, List, Union, Any
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Payoff.ConstantPayoff.constantPayoff import Payoff

class Product(object):
    """This is a class used as API for users. It exposes only useful parameter."""
    
    @staticmethod
    def intervalCoupon(
            couponRate: Real, principal: Real,
            lastPaymentDate: pd.Timestamp,
            nextPaymentDate: pd.Timestamp,
            dayCounter: int = 365
    ) -> Real:
        """
        Returns the amount of interval coupon between two payment dates.
        Principle, coupon rate, and day counter are mandatory.
        """
        td = (nextPaymentDate - lastPaymentDate).days
        return couponRate * principal * td / dayCounter

    @staticmethod
    def updateDayArray(array: Sequence[Real], offset: Real, *more) -> Union[Tuple, List]:
        """
        Parameter array is an ascending array of scalars and offset is a scalar. The function
        returns the positive part of arr - offset. If more is passed in, it also returns
        more[array > offset].
        """
    
        if not offset:
            return array, *more
        nn = []
        for v in array:
            d = v - offset
            if d >= 0:
                nn.append(d)
    
        if more:
            return nn, *(m[len(array) - len(nn):] for m in more)
        return nn

    @staticmethod
    def checkObservationDate(observationDate: Sequence[Any], calendar: Calendar) -> Sequence[pd.Timestamp]:
        """
        Check if all dates in observationDate are trading days. If True, return observationDate
        as-is. Otherwise, it raises ValueError.
        """
        for date in observationDate:
            date = Product.checkIsTrading(date, calendar)
            if not calendar.isTrading(date):
                raise ValueError("%s does not trade" % str(date))
        return observationDate

    @staticmethod
    def checkIsTrading(date: Any, calendar: Calendar) -> pd.Timestamp:
        """Check if *start* is trading."""
        if not isinstance(date, pd.Timestamp):
            raise TypeError("{} is not a pd.Timestamp object".format(date))
        if not calendar.isTrading(date):
            raise ValueError("given non-trading day: {}".format(date))
        return date

    @staticmethod
    def checkPayoff(payoff: Any) -> Payoff:
        """Check if payoff is a *Payoff* object."""
        if not isinstance(payoff, Payoff):
            raise TypeError("payoff must be a Payoff object")
        return payoff

    @staticmethod
    def checkCalendar(calendar: Any) -> Calendar:
        """Check if calendar is a Calendar object."""
        if not isinstance(calendar, Calendar):
            raise TypeError("calendar must be Calendar object")
        return calendar

