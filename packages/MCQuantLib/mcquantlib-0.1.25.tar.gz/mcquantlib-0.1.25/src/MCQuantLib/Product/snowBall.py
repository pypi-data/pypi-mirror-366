import pandas as pd
from scipy.optimize import fsolve
from numpy import array
from numbers import Real
from functools import partial
from typing import Union, Sequence, Optional, Callable, Dict
from MCQuantLib.Engine.engine import Engine
from MCQuantLib.Process.process import Process
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Instrument.AutoCallOption.autocallOption import AutoCallOption
from MCQuantLib.Instrument.BarrierOption.SingleBarrierOption.UpBarrierOption.upBarrierOption import UpOutOption
from MCQuantLib.Payoff.ConstantPayoff.constantPayoff import ConstantPayoff, Payoff
from MCQuantLib.Product.product import Product
from MCQuantLib.Tool.arrayTool import Operation
from MCQuantLib.Tool.dateTool import Calendar


class SnowBall(Product):
    def __init__(
            self, startDate: pd.Timestamp, initialPrice: Real, knockOutBarrier: Union[Sequence, Real],
            knockOutObservationDate: Sequence, knockInBarrier: Union[Sequence, Real], knockInObservationDate: Sequence, knockInPayoff: Payoff,
            knockOutCouponRate: Real, maturityCouponRate: Real,
            calendar: Calendar
    ) -> None:
        """
        A snowball structure is an AutoCall structured product with snowballing
        coupon payments.

        Parameters
        ----------
        startDate : pd.Timestamp
            A pd.Timestamp object indicating the starting day of the
            structured product. It must be a trading as determined by *calendar*
        initialPrice : Real
            The price of the underlying asset on *startDate*.
        knockOutBarrier : Real or Sequence
            The knock-out level of the structure. It can either be
            a scalar or be an array of numbers. If a scalar is passed in, it will be
            treated as the time-invariant barrier level. If an array is passed in,
            it must match the length of *knockOutObservationDate*.
        knockOutObservationDate : Sequence
            The observation dates for knock-out. It must be an array
            of pd.Timestamp objects. All of these dates must be trading dates as
            determined by *calendar*.
        knockInBarrier : Real or Sequence
            Similar to *knockOutBarrier*. It controls the level of knock-in barrier.
        knockInObservationDate : Sequence or "daily"
            similar to *knockOutObservationDate*. *"daily"* indicates daily observation for the
            knock-in event.
        knockInPayoff : Payoff
            Controls payoff which applies when, during the life of the contract,
            a knock-in event occurs while a knock-out does not.
        knockOutCouponRate : Real
            the coupon rate that applies in the event of a knock-out.
        maturityCouponRate : Real
            this rate applies when there is neither knock-out nor knock-in during
            the entire life of the contract.
        calendar : Calendar
            A Calendar object.

        Note
        ----
        The day count convention for coupon payment is *ACT/365*.
        The maturity is ``knockOutObservationDate[-1]``.
        Notional principal is equal to ``initialPrice``.
        """
        _inputs = locals()
        _inputs.pop("self")
        self._inputs = _inputs
        self.calendar = Product.checkCalendar(calendar)
        self.startDate = Product.checkIsTrading(startDate, calendar)
        self.knockInPayoff = Product.checkPayoff(knockInPayoff)
        self.knockOutObservationDate = Product.checkObservationDate(knockOutObservationDate, calendar)
        try:
            self.knockInObservationDate = Product.checkObservationDate(knockInObservationDate, calendar)
        except TypeError:
            if knockInObservationDate != "daily":
                raise ValueError(
                    "knockInObservationDate must either be an array of "
                    "trading days or 'daily, got {}".format(knockInObservationDate)
                )
            else:
                end = knockOutObservationDate[-1]
                knockInObservationDate = calendar.tradingDaysBetween(
                    start=startDate, end=end, endPoint=True
                )[1:]
        self.knockInObservationDate = knockInObservationDate
        self.initialPrice = initialPrice
        self.knockOutBarrier = Operation.fromScalar(knockOutBarrier, knockOutObservationDate)
        self.knockInBarrier = Operation.fromScalar(knockInBarrier, knockInObservationDate)
        self.knockOutCouponRate = knockOutCouponRate
        self.maturityCouponRate = maturityCouponRate
        self.maturityDate = knockOutObservationDate[-1]
        self.observationDayOut = calendar.numTradingDaysBetweenGrid(startDate, knockOutObservationDate)
        self.observationDayIn = calendar.numTradingDaysBetweenGrid(startDate, knockInObservationDate)
        _frozen = partial(
            Product.intervalCoupon, principal=initialPrice,
            lastPaymentDate=startDate
        )
        self._maturityCouponPayment = _frozen(
            couponRate=maturityCouponRate,
            nextPaymentDate=self.maturityDate
        )
        self.notKnockPayoff = ConstantPayoff(self._maturityCouponPayment)
        self.knockOutRebate = [_frozen(
            couponRate=knockOutCouponRate, nextPaymentDate=d
        ) for d in knockOutObservationDate]

        self._frozen = _frozen

    def toStructure(self, valuationDate: pd.Timestamp, spot: Real, knockInFlag: bool) -> InstrumentMC:
        """Return the structure used to value the product."""
        valuationDate = Product.checkIsTrading(valuationDate, self.calendar)
        tradingDayOffset = self.calendar.numTradingDaysBetween(start=self.startDate, end=valuationDate, countEnd=True)
        observationDayOut, rebateOut, barrierOut = Product.updateDayArray(
            self.observationDayOut, tradingDayOffset, self.knockOutRebate, self.knockOutBarrier
        )
        observationDayIn, barrierIn = Product.updateDayArray(
            self.observationDayIn, tradingDayOffset, self.knockInBarrier
        )
        if not knockInFlag:
            obj = AutoCallOption(
                spot=spot, observationDayOut=observationDayOut, rebateOut=rebateOut,
                observationDayIn=observationDayIn, payoffIn=self.knockInPayoff,
                upperBarrierOut=barrierOut, lowerBarrierIn=barrierIn,
                payoffNotKnock=self.notKnockPayoff
            )
        else:
            obj = UpOutOption(
                spot=spot, observationDay=observationDayOut, rebate=rebateOut,
                payoff=self.knockInPayoff, barrier=barrierOut
            )
        return obj

    def value(self, valuationDate: pd.Timestamp, spot: Real, knockInFlag: bool, *args, **kwargs) -> Real:
        """
        Value the product given a date and a spot price. *args* and *kwargs*
        are positional and keyword arguments forwarded to MonteCarlo.calc

        Parameters
        ----------
        valuationDate : pd.Timestamp
            the valuate date. It must be a trading day.
        spot : Real
            the spot price.
        knockInFlag: bool
            whether to mark the product as knock-in. If *True*, the
            structure is an up-and-out option.
        """
        return self.toStructure(valuationDate, spot, knockInFlag).calculateValue(*args, **kwargs)

    def findCouponRate(self, engine: Engine, process: Process, pvTarget: Real,
                       entropy: Optional[int] = None, caller: Optional[Callable] = None) -> Dict:
        """
        Give a target PV, find the coupon rate.

        *entropy* and *caller* are forwarded to MonteCarlo.calc
        """
        e = entropy

        def _call(c):
            nonlocal e
            if e is None:
                e = engine.mostRecentEntropy
            inputs = self._inputs
            inputs['knockOutCouponRate'] = c[0]
            inputs['maturityCouponRate'] = c[0]
            s = self.__class__(**inputs)
            diff = s.value(self.startDate, self.initialPrice, False,
                           engine, process, entropy=e,
                           caller=caller) - pvTarget
            return diff

        rate = fsolve(_call, array([self.knockOutCouponRate]))[0]
        return dict(result=rate, diff=_call([rate]))

