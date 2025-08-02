import numpy as np
import pandas as pd
import QuantLib as ql
from unittest import TestCase
from MCQuantLib.Process.BlackSholes.blackScholes import BlackScholes
from MCQuantLib.Process.Heston.heston import Heston
from MCQuantLib.Tool.dateTool import Calendar
from MCQuantLib.Engine.engine import Engine
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpOutOption
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff
from MCQuantLib.Product.snowBall import SnowBall


class TestProcess(TestCase):
    entropyValue = 12345678
    mcObj = Engine(100, 100)

    def testCalculatePV(self):
        start = pd.Timestamp(2020, 4, 1)
        calendar = Calendar(ql.Japan())
        observationDateOut = calendar.makeScheduleByPeriod(start, "1m", 13)[1:]
        option = SnowBall(
            startDate=start, knockOutObservationDate=observationDateOut, knockOutBarrier=100,
            knockInObservationDate="daily", knockInBarrier=80, knockOutCouponRate=0.16,
            knockInPayoff=-PlainVanillaPayoff(strike=100, optionType=-1), maturityCouponRate=0.16,
            initialPrice=100, calendar=calendar
        )
        res = {}
        for xi in [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5]:
            hestonObj = Heston(.015, 0, -.07879, .05254, 13.2154, xi, .05254, 252)
            print('Coupon of Snow Ball Option:', option.findCouponRate(process=hestonObj, pvTarget=0, engine=self.mcObj))
            value = option.value(spot=100, valuationDate=start, knockInFlag=False, engine=self.mcObj, process=hestonObj, entropy=self.entropyValue)
            res[xi] = value
        print('PV at different VolVol:', res)

    def testHeston(self):
        blackScholesObj = BlackScholes(0.017, 0, 0.2991, 252)
        hestonObj = Heston(0.017, 0, -0.07196, 0.0625, 13.3601, 1.0394,  0.08946, 252)
        optionObj = UpOutOption(spot=100, rebate=0, barrier=100000, observationDay=np.array(range(1, 253)), payoff=PlainVanillaPayoff(strike=100, optionType=1))
        print('BS PV: ', optionObj.calculateValue(self.mcObj, blackScholesObj, entropy=self.entropyValue))
        print('Heston PV', optionObj.calculateValue(self.mcObj, hestonObj, entropy=self.entropyValue))

