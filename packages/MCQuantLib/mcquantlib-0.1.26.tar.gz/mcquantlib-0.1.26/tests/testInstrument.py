import numpy as np
from unittest import TestCase
from MCQuantLib.Instrument.BarrierOption.DoubleBarrierOption.doubleBarrierOption import DoubleOutOption
from MCQuantLib.Payoff.ConstantPayoff.constantPayoff import ConstantPayoff
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpOutOption
from MCQuantLib.Instrument.AutoCallOption.autocallOption import AutoCallOption
from MCQuantLib.Process.Heston.heston import Heston
from MCQuantLib.Process.BlackSholes.blackScholes import BlackScholes
from MCQuantLib.Engine.engine import Engine


class TestInstrument(TestCase):
    denseDayArray = np.array(range(1, 253))
    sparseDayArray = np.array(range(21, 253, 21))
    snowballingRebate = np.linspace(15 / 12, 15, 12)
    entropyValue = 12345678
    mc = Engine(100, 100000)
    bs = BlackScholes(0.03, 0, 0.25, 252)
    hst = Heston(.03, 0, 0, .0625, 1, .2, .0625, 252)

    def testSnowBallValue(self):
        snowBallObj = AutoCallOption(
            spot=100,
            upperBarrierOut=105,
            observationDayOut=self.sparseDayArray,
            rebateOut=self.snowballingRebate,
            lowerBarrierIn=80,
            observationDayIn=self.denseDayArray,
            payoffIn=-PlainVanillaPayoff(strike=100, optionType=-1),
            payoffNotKnock=ConstantPayoff(amount=15),
        )
        print('snow ball self.hst: ', snowBallObj.calculateValue(self.mc, self.hst, entropy=self.entropyValue))
        print('snow ball self.bs: ', snowBallObj.calculateValue(self.mc, self.bs, entropy=self.entropyValue))

    def testUpOut(self):
        from time import time
        upOutObj = UpOutOption(
            spot=100, rebate=0, barrier=120, observationDay=np.array(range(1, 127)),
            payoff=PlainVanillaPayoff(strike=100, optionType=1)
        )
        t0 = time()
        print('up out self.bs: ', upOutObj.calculateValue(self.mc, self.bs, entropy=self.entropyValue))
        print(time() - t0)

    def testDoubleOut(self):
        doubleOut = DoubleOutOption(
            spot=100,
            barrierUp=120,
            barrierDown=80,
            observationDayUp=self.denseDayArray,
            observationDayDown=self.sparseDayArray,
            payoff=PlainVanillaPayoff(strike=100, optionType=1),
            rebateUp=3,
            rebateDown=2
        )
        print('double out self.bs: ', doubleOut.calculateValue(self.mc, self.bs, entropy=self.entropyValue))
