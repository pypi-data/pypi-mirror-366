import numpy as np
from unittest import TestCase
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.singleBarrierOption import SingleBarrierCreator


class TestCreator(TestCase):
    denseDayArray = np.array(range(1, 253))
    sparseDayArray = np.array(range(21, 253, 21))
    barrier = SingleBarrierCreator(
        level=104.99,
        observationDay=sparseDayArray,
        upOrDown="up",
        rebate=0,
        payoff=PlainVanillaPayoff(strike=100, optionType=1)
    )

    paths = np.array(
        [[95, 101, 99, 104, 99, 95, 97, 96, 95, 106, 97, 98],
         [99, 103, 98, 101, 101, 98, 99, 97, 99, 98, 99, 101],
         [106, 103, 105, 102, 100, 101, 104, 102, 96, 95, 99, 96],
         [101, 100, 103, 105, 104, 99, 101, 97, 105, 105, 100, 106],
         [97, 96, 97, 100, 97, 97, 95, 96, 105, 98, 95, 104],
         [99, 99, 105, 98, 99, 105, 96, 99, 105, 98, 96, 102],
         [101, 95, 96, 102, 102, 101, 95, 105, 101, 106, 100, 102],
         [102, 103, 97, 106, 104, 105, 97, 98, 95, 98, 100, 96],
         [96, 102, 103, 97, 100, 104, 104, 95, 101, 96, 100, 102],
         [96, 95, 104, 98, 99, 102, 104, 106, 105, 95, 101, 95]]
    )

    discountFactor = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    def testOutBarrier(self):
        print(self.barrier.filter(self.paths, self.discountFactor))

    def testFill(self):
        print(self.barrier.fill(self.denseDayArray, np.inf).level)

    def testToLog(self):
        logBarrier = self.barrier.toLog(100)
        logPath = np.log(self.paths / 100)
        self.assertTrue(
            self.barrier.filter(self.paths, self.discountFactor)['PV'] == logBarrier.filter(logPath, self.discountFactor)['PV']
        )
