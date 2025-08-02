# MCQuantLib

## Introduction

MCQuantLib is a derivative of Quantlib, 
a famous quantitative library of financial engineering. 
Unlike QuantLib, however, MCQuantLib focuses on Monte 
Carlo simulation in option pricing. It provides 
different kinds of Payoffs, Structures, Product 
models and Calendar Tools.

## Why Another Monte Carlo Pricing Library

The first reason is that all handles and quotes in QuantLib
make it very difficult to maintain a robust option pricing project.
MCQuantLib is designed to **simplify** the whole procedure of pricing, enhance
**stability** and provides **user-friendly** API.

The second reason is that calendar state is usually global in QuantLib, which 
will creates huge problems when you have couples of options for revaluation.
Updating even one date may be time-consuming and may not render to correct results.
MCQuantLib avoids using global date and calendar, suitable for pricing and
re-valuating **portfolio of options**.

The third reason is that QuantLib focuses on continuously observed options, while
MCQuantLib focuses on **discretely observed options**. This is a great difference because
price of options may be different even if they have the same name in QuantLib and MCQuantLib.

The fourth reason is that MCQuantLib is much **faster** than Monte Carlo Engines provided by
QuantLib. MCQuantLib is based on numpy and can use multiple CPU cores to simulate paths.
Almost every function in MCQuantLib is fine-tuned and optimized for speed. For vanilla option, 
MCQuantLib can simulate 10^8 paths in 56s, or 10^6 paths in 3.4s, or 10^5 paths in 3s.

## Important Notice

If you are using python on Windows system, to unleash full power of MCQuantLib, you have to run
powershell or terminal by **administrator privileges**. Then run your python script by:

    python yourScript.py

Running without administrator privileges will force ``joblib`` to fall back into single-process mode and
not to really perform multi-process computing.

## Install

Use ``pip install MCQuantLib`` to install.

## Usage

### Import

You should always import stochastic process module and monte carlo engine module before any pricing:

    from MCQuantLib import Engine, BlackScholes, Heston
    batchSize = 100
    numIteration = 900
    r = 0.03
    q = 0
    v = 0.25
    dayCounter = 252
    mc = Engine(batchSize, numIteration)
    bs = BlackScholes(r, q, v, dayCounter)

### Option Name

MCQuantLib supports coding by two kinds of style, one is called as ``Academy Style`` and
another is called as ``QuantLib Style``. The difference between them is the ``Academy Style`` coding
uses array and pure number to represent dates, while ``QuantLib Style`` uses ``calendar`` and ``pandas.Timestamp``
to mark dates.

To use ``Academy Style``, you should import the class with ``Option`` suffix, such as ``VanillaCallOption`` 
and ``UpOutOption``. To use ``QuantLib Style``, you should import the class without ``Option`` suffix, such
as ``VanillaCall`` and ``UpOut``.

### Vanilla Call Option

To price a vanilla Call Option, use:

    from MCQuantLib import VanillaCallOption
    option = VanillaCallOption(
        spot=100,
        observationDay=np.linspace(1, 252, 252),
        strike=100
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import VanillaCall, Calendar
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    observationDate = calendar.makeScheduleByPeriod(start, '1d', 253, True)[1:]
    option = VanillaCall(start, observationDate, strike=100, calendar=calendar)
    option.value(start, 100, mc, bs)

### Vanilla Put Option

To price a vanilla Put Option, use:

    from MCQuantLib import VanillaPutOption
    option = VanillaPutOption(
        spot=100,
        observationDay=np.linspace(1, 252, 252),
        strike=100
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import VanillaPut, Calendar
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    observationDate = calendar.makeScheduleByPeriod(start, '1d', 253, True)[1:]
    option = VanillaPut(start, observationDate, strike=100, calendar=calendar)
    option.value(start, 100, mc, bs)

### Barrier Option

Barrier Option in MCQuantLib is different with those in QuantLib, even they may
have the same name. All Barrier Options in QuantLib are *continuously observed*, while
barrier options in MCQuantLib are all *discretely observed*. For knock-out options, discretely
observed option usually has higher price than continuously observed ones. For knock-in options, 
discretely observed option usually has lower price than continuously observed ones.

### Up-Out Option

To price a vanilla Up-Out Barrier Option, use:

    from MCQuantLib import UpOutOption, PlainVanillaPayoff
    option = UpOutOption(
        spot=100,
        barrier=120,
        rebate=0,
        observationDay=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1, strike=100)
    )
    option.calculateValue(mc, bs, requestGreek=True)

For time-varying barrier and rebate, pass in an array to *barrier*:

    from MCQuantLib import UpOutOption, PlainVanillaPayoff
    optionTimeVaryingBarrier = UpOutOption(
        spot=100,
        barrier=np.linspace(110, 120, 252),
        rebate=np.linspace(0, 3, 252),
        observationDay=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1, strike=100)
    )
    optionTimeVaryingBarrier.calculateValue(mc, bs)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import UpOut, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockOutObservationDate = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    option = UpOut(start, 120, 10, knockOutObservationDate, payoff=PlainVanillaPayoff(strike=100, optionType=1),calendar=calendar)
    option.value(start, 100, mc, bs)

### Up-In Option

To price a vanilla Up-In Barrier Option, use:

    from MCQuantLib import UpInOption, PlainVanillaPayoff
    option = UpInOption(
        spot=100,
        barrier=120,
        rebate=0,
        observationDay=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1,strike=100)
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import UpIn, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockOutObservationDate = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    option = UpIn(start, 120, 10, knockOutObservationDate, payoff=-PlainVanillaPayoff(strike=100, optionType=-1),calendar=calendar)
    option.value(start, 100, mc, bs)

### Down-Out Option

To price a vanilla Down-Out Barrier Option, use:

    from MCQuantLib import DownOutOption, PlainVanillaPayoff
    option = DownOutOption(
        spot=100,
        barrier=80,
        rebate=0,
        observationDay=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1, strike=100)
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import DownOut, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockOutObservationDate = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    option = DownOut(start, 87, 10, knockOutObservationDate, payoff=PlainVanillaPayoff(strike=100, optionType=-1),calendar=calendar)
    option.value(start, 100, mc, bs)

### Down-In Option

To price a vanilla Down-In Barrier Option, use:

    from MCQuantLib import DownInOption, PlainVanillaPayoff
    option = DownInOption(
        spot=100,
        barrier=80,
        rebate=0,
        observationDay=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1, strike=100)
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import DownIn, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockOutObservationDate = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    option = DownIn(start, 87, 10, knockOutObservationDate, payoff=-PlainVanillaPayoff(strike=100, optionType=-1),calendar=calendar)
    option.value(start, 100, mc, bs)

### Double-Out Option

To price a vanilla Double-Out Barrier Option, use:
    
    from MCQuantLib import DoubleOutOption, PlainVanillaPayoff
    option = DoubleOutOption(
        spot=100,
        barrierUp=120,
        barrierDown=80,
        observationDayUp=np.linspace(1, 252, 252),
        observationDayDown=np.linspace(1, 252, 252),
        payoff=PlainVanillaPayoff(optionType=1, strike=100),
        rebateUp=1,
        rebateDown=2
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import DoubleOut, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockOutObservationDateUp = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    knockOutObservationDateDown = calendar.makeScheduleByPeriod(start, '2M', 7, True)[1:]
    option = DoubleOut(
        spot=100,
        barrierUp=120,
        barrierDown=80,
        observationDayUp=knockOutObservationDateUp,
        observationDayDown=knockOutObservationDateDown,
        payoff=PlainVanillaPayoff(strike=100, optionType=1),
        rebateUp=3,
        rebateDown=2
    )
    option.value(start, 100, mc, bs)

### Double-In Option

To price a vanilla Double-In Barrier Option, use:

    from MCQuantLib import DoubleInOption, PlainVanillaPayoff
    option = DoubleInOption(
        spot=100,
        barrierUp=120,
        barrierDown=80,
        observationDayUp=np.linspace(1, 252, 21),
        observationDayDown=np.linspace(1, 252, 252),
        rebate=2,
        payoff=PlainVanillaPayoff(optionType=1, strike=100)
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:
    
    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import DoubleIn, Calendar, PlainVanillaPayoff
    calendar = Calendar(ql.Japan())
    start = pd.Timestamp(2024, 7, 9)
    knockInObservationDateUp = calendar.makeScheduleByPeriod(start, '1M', 13, True)[1:]
    knockInObservationDateDown = calendar.makeScheduleByPeriod(start, '2M', 7, True)[1:]
    option = DoubleIn(
        spot=100,
        barrierUp=120,
        barrierDown=80,
        observationDayUp=knockInObservationDateUp,
        observationDayDown=knockInObservationDateDown,
        payoff=PlainVanillaPayoff(strike=100, optionType=1),
        rebateUp=3,
        rebateDown=2
    )
    option.value(start, 100, mc, bs)

### SnowBall Option

To price a Snow Ball Option, use:

    from MCQuantLib import SnowBallOption
    option = SnowBallOption(
        spot=100,
        upperBarrierOut=105,
        lowerBarrierIn=80,
        observationDayIn=np.linspace(1, 252, 252),
        observationDayOut=np.linspace(1, 252, 12),
        rebateOut=np.linspace(1, 15, 12),
        fullCoupon=15
    )
    option.calculateValue(mc, bs, requestGreek=True)

If you prefer a ``QuantLib Style`` and want to use calendar object:

    import pandas as pd
    import QuantLib as ql
    from MCQuantLib import SnowBall, PlainVanillaPayoff, Calendar
    # instantiate a Calendar object so you can use it to generate periodic pd.Timestamp array
    calendar = Calendar(ql.Japan())
    # this should be a trading day
    start = pd.Timestamp(2024, 7, 9)
    assert calendar.isTrading(start)
    # monthly trading dates excluding the start
    monthlyDates = calendar.makeScheduleByPeriod(start, "1m", 13)[1:]
    # a short put payoff
    shortPut = - PlainVanillaPayoff(optionType=-1, strike=100)
    # instantiate the structured product
    option = SnowBall(
        startDate=start, initialPrice=100, knockOutBarrier=105,
        knockOutObservationDate=monthlyDates, knockInBarrier=80, knockInObservationDate="daily",
        knockInPayoff=shortPut, knockOutCouponRate=0.15,
        maturityCouponRate=0.15, calendar=calendar
    )
    # value the contract given day and spot price
    option.value(pd.Timestamp(2024, 8, 8), 102, False, mc, bs)

### Caller

Caller is used to decide how to parallel your Monte Carlo simulation. It is an attribute function of ``Engine`` object. The default caller is roughly equivalent to:

    def caller(calc, seedSequence, /, **kwargs):
        calc = joblib.delayed(calc)
        kwargs["n_jobs"] = cpu_counts() if "n_jobs" not in kwargs else kwargs["n_jobs"]
        with joblib.Parallel(**kwargs) as parallel:
            res = parallel(calc(seed) for seed in seedSequence)
        return res
    
To implement Monte Carlo with your own caller, for example one with no parallel computation, define the caller as follows:

    def selfDefinedCaller(calc, seedSequence):
        return [calc(s) for s in seedSequence]
    
You may also set the default caller so that you do not need to specify ``caller`` every time ``calculate`` is called.

    mc.caller = selfDefinedCaller
    
To revert to the joblib caller, delete the caller or set it to ``None``:

    del mc.caller
    mc.caller == None  # True

### Process

Besides Black-Scholes process, MCQuantLib also provides Heston process to
simulate market dynamic. To use Heston model to price your option, you should 
first create a Heston process object, and pass it as parameter of ``value`` or ``calculateValue``
function. For example:

    from MCQuantLib import Heston
    hst = Heston(0.017, 0, -0.07196, 0.0625, 13.3601, 1.0394, 0.08946, 252)
    # ... There is a lot of other codes here
    option.value(start, 100, mc, hst)
    # or you can:
    option.calculateValue(mc, hst, requestGreek=True)

### Self-Defined Option

To price a self-defined option, the only thing you need to do
is to inherit from class ``InstrumentMC`` and overwrite ``_setSpot``
and ``pvLogPath``. You should also make sure your self-defined class
has attribute named as ``_simulatedTimeArray``. We will introduce these
attributes as follows:

#### Inherit

You should create new class like:
    
    import numpy as np
    from numbers import Number
    from MCQuantLib import InstrumentMC
    class SelfDefinedOption(InstrumentMC):
        def __init__(self, spot: Number, observationDay: np.ndarray, optionParameter: Any):
            self._spot = spot
            self.observationDay = observationDay
            self._simulatedTimeArray = np.append([0], observationDay)
            self.optionParameter = optionParameter

Class ``InstrumentMC`` does not has ``__init__`` function.
So you have to write your own one. It is important to make 
sure you have ``spot`` as a parameter of ``__init__``. 

Your class must declare ``_simulatedTimeArray`` attribute in ``__init__``. 
This parameter tells MCQuantLib how to handle date. The random generator will generate
random numbers according to this array. By default, the last element of ``_simulatedTimeArray`` will
be the expiration day. Also, for ``__init__`` function, You should have at least one parameter named 
as ``observationDay``, typed as ``np.ndarray``, because it is the base of your ``_simulatedTimeArray``. 
By default, you should write it in ``__init__`` as:
    
    def __init__(self, spot: Number, observationDay: np.ndarray, optionParameter: Any):
        # ...
        self._simulatedTimeArray = np.append([0], observationDay)

#### Attribute Function: pvLogPath

This is the most important function when pricing your self-defined option.
It accepts logPath array and discountFactor array, and returns a scalar as 
price of this option. For vanilla option, this function looks like:

    def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Number:
        discountFactorTerminal = discountFactor[-1]
        payoffTerminal = self.payoff(np.exp(logPath[:, -1]) * self.spot)
        return np.sum(payoffTerminal * discountFactorTerminal) / len(logPath)

Make sure you understand the mean discounted value of payoff in every path should be
the price of your option. Based on this fact, you should design your own ``pvLogPath``.

#### Example

Let's show an example to price a self-defined option. This option will give you payoff
as ``max(pricePath) - min(pricePath)``. If price of the stock goes as high as ``135`` at some
time before expiration day, and goes as low as ``87`` at another time. This option will give you ``135 - 87`` at expiration
day. Let's call it as MaxMinOption and price it:
    
    import numpy as np
    from numbers import Number
    from MCQuantLib import InstrumentMC
    class MaxMinOption(InstrumentMC):
        def __init__(self, spot: Number, observationDay: np.ndarray):
            self._spot = spot
            self.observationDay = observationDay
            self._simulatedTimeArray = np.append([0], observationDay)
    
        def pvLogPath(self, logPath: np.ndarray, discountFactor: np.ndarray) -> Number:
            discountFactorTerminal = discountFactor[-1]
            price = np.exp(logPath) * self.spot
            maxPrice = np.max(price, axis=1)
            minPrice = np.min(price, axis=1)
            payoffTerminal = maxPrice - minPrice
            return np.sum(payoffTerminal * discountFactorTerminal) / len(logPath)

Then import necessary module before price it:

    from MCQuantLib import Engine, BlackScholes
    batchSize = 100
    numIteration = 900
    r = 0.03
    q = 0
    v = 0.25
    dayCounter = 252
    mc = Engine(batchSize, numIteration)
    bs = BlackScholes(r, q, v, dayCounter)

The last thing is creating an object and price it:

    maxMin = MaxMinOption(100, np.array(range(1, 253)))
    maxMin.calculateValue(mc, bs, requestGreek=True)

