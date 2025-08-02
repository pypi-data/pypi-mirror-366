import pandas as pd
import QuantLib as ql
from unittest import TestCase
from functools import partial
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff
from MCQuantLib.Process.BlackSholes.blackScholes import BlackScholes
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Engine.engine import Engine
from MCQuantLib.Product.snowBall import SnowBall


class TestProduct(TestCase):
    entropyValue = 12345678
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2019, 1, 31)
    knockOutObservationDate = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    mcObj = Engine(100, 1000)
    blackScholesObj = BlackScholes(0.03, 0, 0.265, 252)
    option = SnowBall(
        startDate=start, knockOutObservationDate=knockOutObservationDate, knockOutBarrier=105,
        knockInObservationDate="daily", knockInBarrier=70, knockOutCouponRate=0.09202428093544388,
        knockInPayoff=-PlainVanillaPayoff(strike=100, optionType=-1), maturityCouponRate=0.09202428093544388,
        initialPrice=100, calendar=calendar
    )
    def testCalculate(self):
        import time
        s = time.time()
        print('snow ball bs:', self.option.value(self.start, 100, False, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))
        print('snow ball pricing time used:', time.time() - s)

    def testAssertTradingDay(self):
        value1 = partial(self.option.value, spot=100, knockInFlag=False, engine=self.mcObj, process=self.blackScholesObj)
        with self.assertRaises(ValueError):
            value1(pd.Timestamp(2019, 5, 1))

    def testKnockIn(self):
        from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpOutOption
        from MCQuantLib.Instrument.AutoCallOption.autocallOption import AutoCallOption
        self.assertIsInstance(self.option.toStructure(pd.Timestamp(2019, 5, 7), 100, True), UpOutOption)
        self.assertIsInstance(self.option.toStructure(pd.Timestamp(2019, 5, 7), 100, False), AutoCallOption)

    def testAveragePrice(self):
        from MCQuantLib.Product.averagePrice import AveragePrice
        a = AveragePrice(self.start, self.knockOutObservationDate, 1, 100, self.calendar)
        print('average price option in bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testAverageStrike(self):
        from MCQuantLib.Product.averageStrike import AverageStrike
        a = AverageStrike(self.start, self.knockOutObservationDate, 1, self.calendar)
        print('average strike option in bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testUpIn(self):
        from MCQuantLib.Product.upIn import UpIn
        a = UpIn(self.start, 120, 10, self.knockOutObservationDate, payoff=-PlainVanillaPayoff(strike=100, optionType=-1),calendar=self.calendar)
        print('up in bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testDownIn(self):
        from MCQuantLib.Product.downIn import DownIn
        a = DownIn(self.start, 87, 10, self.knockOutObservationDate, payoff=-PlainVanillaPayoff(strike=100, optionType=-1),calendar=self.calendar)
        print('down in bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testUpOut(self):
        from MCQuantLib.Product.upOut import UpOut
        a = UpOut(self.start, 120, 10, self.knockOutObservationDate, payoff=PlainVanillaPayoff(strike=100, optionType=1),calendar=self.calendar)
        print('up out bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testDownOut(self):
        from MCQuantLib.Product.downOut import DownOut
        a = DownOut(self.start, 87, 10, self.knockOutObservationDate, payoff=PlainVanillaPayoff(strike=100, optionType=-1),calendar=self.calendar)
        print('down out bs:', a.value(self.start,100, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))

    def testFindCoupon(self):
        print('snow ball coupon:', self.option.findCouponRate(self.mcObj, self.blackScholesObj, 0, entropy=self.entropyValue))

    def testMCCaller(self):

        def nonsense(calc, seeds):
            return [1]*len(seeds)

        self.mcObj.caller = nonsense
        print('snow ball nonsense:', self.option.value(pd.Timestamp(2019, 5, 7), 100, False, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))
        del self.mcObj.caller
        print('snow ball caller:', self.option.value(pd.Timestamp(2019, 5, 7), 100, False, self.mcObj, self.blackScholesObj, entropy=self.entropyValue))
