import numpy as np
from unittest import TestCase
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff


class TestPayoff(TestCase):
    def testPayoff(self):
        payoff = PlainVanillaPayoff(strike=50, optionType=-1)
        prices = np.linspace(5, 100, 21)
        self.assertTrue(np.all(payoff(prices) == PlainVanillaPayoff(strike=50, optionType=-1)(prices)))

    def testPayoffNegative(self):
        payoff = -PlainVanillaPayoff(strike=50, optionType=-1)
        prices = np.linspace(5, 100, 21)
        self.assertTrue(np.all(payoff(prices) == -PlainVanillaPayoff(strike=50, optionType=-1)(prices)))

    def testPayoffAdd(self):
        added = PlainVanillaPayoff(strike=50, optionType=-1) + \
            PlainVanillaPayoff(strike=50, optionType=1)
        prices = np.linspace(5, 100, 21)
        self.assertTrue(np.all(added(prices) == PlainVanillaPayoff(strike=50, optionType=1)(prices) +
                               PlainVanillaPayoff(strike=50, optionType=-1)(prices)))
