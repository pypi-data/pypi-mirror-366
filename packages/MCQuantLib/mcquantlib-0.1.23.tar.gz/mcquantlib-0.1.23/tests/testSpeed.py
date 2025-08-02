import time
import pandas as pd
import QuantLib as ql
from unittest import TestCase
from MCQuantLib.Engine.engine import Engine
from MCQuantLib.Process.Heston.heston import Heston
from MCQuantLib.Process.BlackSholes.blackScholes import BlackScholes


class TestSpeed(TestCase):
    batchSize = 100
    numIteration = 10000
    requiredSamples = batchSize * numIteration
    
    def testVanillaQLByBS(self):
        """This takes about 18s."""
        calendar = ql.Japan()
        todayDate = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = todayDate

        spotPrice = 100
        strikePrice = 100
        volatility = 0.2
        riskFreeRate = 0.02
        maturityDate = calendar.advance(todayDate, ql.Period(1, ql.Years))
        dayCounter = ql.Business252(calendar)

        optionType = ql.Option.Call
        exercise = ql.EuropeanExercise(maturityDate)
        payoff = ql.PlainVanillaPayoff(optionType, strikePrice)
        europeanOption = ql.VanillaOption(payoff, exercise)

        spotHandle = ql.QuoteHandle(ql.SimpleQuote(spotPrice))
        flatTS = ql.YieldTermStructureHandle(ql.FlatForward(todayDate, riskFreeRate, dayCounter))
        flatVolTS = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(todayDate, calendar, volatility, dayCounter))
        dividendYield = ql.YieldTermStructureHandle(ql.FlatForward(todayDate, 0.0, dayCounter))

        bs = ql.BlackScholesMertonProcess(spotHandle, dividendYield, flatTS, flatVolTS)
        mc = ql.MCEuropeanEngine(bs,"pseudorandom", timeSteps=1, requiredSamples=self.requiredSamples)
        europeanOption.setPricingEngine(mc)

        t0 = time.time()
        optionPrice = europeanOption.NPV()
        print('Time of QuantLib MC with BS model:', time.time()-t0)
        print(f"Price of vanilla call with BS model: {optionPrice:.4f}")

    def testVanillaMLByBS(self):
        """This takes about 3s."""
        from MCQuantLib.Product.vanillaCall import VanillaCall, Calendar
        calendar = Calendar(ql.Japan())
        todayDate = pd.Timestamp.now()
        observationDate = calendar.makeScheduleByPeriod(todayDate, '1y', 2)
        europeanOption = VanillaCall(todayDate, observationDate, 100, calendar)
        bs = BlackScholes(0.02, 0, 0.2, 252)
        mc = Engine(self.batchSize, self.numIteration)

        t0 = time.time()
        optionPrice = europeanOption.value(todayDate, 100, mc, bs)
        print('Time of MCQuantLib MC with BS model:', time.time()-t0)
        print(f"Price of vanilla call with BS model: {optionPrice:.4f}")

    def testVanillaQLByHeston(self):
        """This takes about 18s."""
        calendar = ql.Japan()
        todayDate = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = todayDate

        spotPrice = 100
        strikePrice = 100
        volatility = 0.2
        riskFreeRate = 0.02
        maturityDate = calendar.advance(todayDate, ql.Period(1, ql.Years))
        dayCounter = ql.Business252(calendar)

        optionType = ql.Option.Call
        exercise = ql.EuropeanExercise(maturityDate)
        payoff = ql.PlainVanillaPayoff(optionType, strikePrice)
        europeanOption = ql.VanillaOption(payoff, exercise)

        spotHandle = ql.QuoteHandle(ql.SimpleQuote(spotPrice))
        flatTS = ql.YieldTermStructureHandle(ql.FlatForward(todayDate, riskFreeRate, dayCounter))
        dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(todayDate, 0.0, dayCounter))

        v0 = volatility * volatility
        kappa = 1.0
        theta = v0
        sigma = 0.5
        rho = -0.7

        hst = ql.HestonProcess(flatTS, dividendTS, spotHandle, v0, kappa, theta, sigma, rho)
        mc = ql.MCEuropeanHestonEngine(hst,"pseudorandom", timeSteps=1, requiredSamples=self.requiredSamples)
        europeanOption.setPricingEngine(mc)

        t0 = time.time()
        optionPrice = europeanOption.NPV()
        print('Time of QuantLib MC with Heston model:', time.time()-t0)
        print(f"Price of vanilla call with Heston model: {optionPrice:.4f}")

    def testVanillaMLByHeston(self):
        """This takes about 3s."""
        from MCQuantLib.Product.vanillaCall import VanillaCall, Calendar
        calendar = Calendar(ql.Japan())
        todayDate = pd.Timestamp.now()
        observationDate = calendar.makeScheduleByPeriod(todayDate, '1y', 2)
        europeanOption = VanillaCall(todayDate, observationDate, 100, calendar)

        riskFreeRate = 0.02
        volatility = 0.2
        v0 = volatility * volatility
        kappa = 1.0
        theta = v0
        sigma = 0.5
        rho = -0.7
        hst = Heston(riskFreeRate, 0, rho, theta, kappa, sigma, v0, 252)
        mc = Engine(self.batchSize, self.numIteration)

        t0 = time.time()
        optionPrice = europeanOption.value(todayDate, 100, mc, hst)
        print('Time of MCQuantLib MC with Heston model:', time.time()-t0)
        print(f"Price of vanilla call with Heston model: {optionPrice:.4f}")

