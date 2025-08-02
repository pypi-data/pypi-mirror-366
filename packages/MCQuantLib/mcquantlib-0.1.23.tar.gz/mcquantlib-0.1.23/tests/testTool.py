import numpy as np
import pandas as pd
import QuantLib as ql
from unittest import TestCase
from MCQuantLib import Calendar


class TestTool(TestCase):
    def testVectorize(self):
        def pyfunc(s, k):
            return s - k if s > k else 0
        func = np.vectorize(pyfunc, otypes=[float])
        print(func(np.linspace(1, 100, 100), 50))

    def testCalendar(self):
        calendar = Calendar(ql.Japan())
        # self.start date of the contract
        startDate = pd.Timestamp(2019, 1, 31)
        assert calendar.isTrading(startDate)
        # knock-out observation days
        knockOutObservationDate = calendar.makeScheduleByPeriod(start=startDate, period="2m", count=13, forwardAdjust=True)[1:]
        print(np.array(knockOutObservationDate))
