import numpy as np
from numbers import Real
from joblib import Parallel, delayed
from joblib import wrap_non_picklable_objects
from typing import Dict, Optional, Callable, Sequence, Union, Tuple
from multiprocessing import cpu_count
from MCQuantLib.Instrument.instrument import InstrumentMC
from MCQuantLib.Process.process import Process, ProcessMC


class Engine(object):
    finiteDifferenceDict = {'central': 0, 'forward': 1, 'backward': -1}

    @staticmethod
    def finiteDifferenceType(fdType: Union[str, int]) -> int:
        if type(fdType) is str:
            return Engine.finiteDifferenceDict[fdType]
        elif type(fdType) is int:
            return fdType
        else:
            raise ValueError("Finite Difference type is not validated: %s" % str(fdType))

    @staticmethod
    def calculateShift(fdStep: Optional[Dict[str, Real]] = None, fdType: Optional[Dict[str, int]] = None) -> (Real, Real, Real, int, int, int, Real):
        fdStep = dict(ds=0.01, dr=0.0001, dv=0.01) if fdStep is None else fdStep
        fdType = dict(Delta=0, Rho=0, Vega=0) if fdType is None else {k:Engine.finiteDifferenceType(fdType[k]) for k in fdType}
        ds, dr, dv = fdStep['ds'], fdStep['dr'], fdStep['dv']
        dsFdType, drFdType, dvFdType = fdType['Delta'], fdType['Rho'], fdType['Vega']
        dsSquare = ds * ds
        return dict(ds=ds, dr=dr, dv=dv, dsFdType=dsFdType, drFdType=drFdType, dvFdType=dvFdType, dsSquare=dsSquare)

    @staticmethod
    def calculatePV(coordinator: ProcessMC, discountFactor: np.ndarray, option: InstrumentMC, batchSize: int, seed: int) -> Real:
        eps = coordinator.generateEps(seed, batchSize)
        path = coordinator.pathGivenEps(eps)
        return option.pvLogPath(path, discountFactor)

    @staticmethod
    def calculateDelta(dsFdType: int, ds: Real, spot: Real, pvSpotPlus: Real, pv: Real, pvSpotMinus: Real) -> Real:
        if dsFdType == 0:
            delta = (pvSpotPlus - pvSpotMinus) / (2 * ds) / spot
        elif dsFdType == 1:
            delta = (pvSpotPlus - pv) / ds / spot
        else:
            delta = (pv - pvSpotMinus) / ds / spot
        return delta

    @staticmethod
    def calculateGamma(dsSquare: Real, spot: Real, pvSpotPlus: Real, pv: Real, pvSpotMinus: Real) -> Real:
        return (pvSpotPlus + pvSpotMinus - 2 * pv) / (dsSquare * spot * spot)

    @staticmethod
    def calculateRho(drFdType: int, dr: Real, option: InstrumentMC, shiftedPath: Dict[str, np.ndarray], pv: Real) -> Real:
        if drFdType == 0:
            pvRatePlus = option.pvLogPath(shiftedPath['R plus'], shiftedPath['DF plus'])
            pvRateMinus = option.pvLogPath(shiftedPath['R minus'], shiftedPath['DF minus'])
            rho = (pvRatePlus - pvRateMinus) / (2 * dr)
        elif drFdType == 1:
            pvRatePlus = option.pvLogPath(shiftedPath['R plus'], shiftedPath['DF plus'])
            rho = (pvRatePlus - pv) / dr
        else:
            pvRateMinus = option.pvLogPath(shiftedPath['R minus'], shiftedPath['DF minus'])
            rho = (pv - pvRateMinus) / dr
        return rho

    @staticmethod
    def calculateVega(dvFdType: int, dv: Real, option: InstrumentMC, shiftedPath: Dict[str, np.ndarray], pv: Real, discountFactor: np.ndarray) -> Real:
        if dvFdType == 0:
            pvVolPlus = option.pvLogPath(shiftedPath['V plus'], discountFactor)
            pvVolMinus = option.pvLogPath(shiftedPath['V minus'], discountFactor)
            vega = (pvVolPlus - pvVolMinus) / (2 * dv)
        elif dvFdType == 1:
            pvVolPlus = option.pvLogPath(shiftedPath['V plus'], discountFactor)
            vega = (pvVolPlus - pv) / dv
        else:
            pvVolMinus = option.pvLogPath(shiftedPath['V minus'], discountFactor)
            vega = (pv - pvVolMinus) / dv
        return vega

    @staticmethod
    def calculateTheta(option: InstrumentMC, shiftedPath: Dict[str, np.ndarray], pv: Real, dayCounter: int) -> Real:
        pvNextDay = option.pvLogPath(shiftedPath['Paths next day'], shiftedPath['DF next day'])
        theta = (pvNextDay - pv) / dayCounter
        return theta

    @staticmethod
    def calculatePVWithGreek(coordinator: ProcessMC, discountFactor: np.ndarray, option: InstrumentMC, batchSize: int, seed: int, process: Process, spot: Real, ds: Real, dr: Real, dv: Real, dsFdType: int, drFdType: int, dvFdType: int, dsSquare: Real) -> Tuple[Real, Real, Real, Real, Real, Real]:
        eps = coordinator.generateEps(seed, batchSize)
        basePath = coordinator.pathGivenEps(eps)
        shiftedPath = coordinator.shift(path=basePath, ds=ds, dr=dr, dv=dv, eps=eps)

        pv = option.pvLogPath(basePath, discountFactor)
        pvSpotPlus = option.pvLogPath(shiftedPath['S plus'], discountFactor)
        pvSpotMinus = option.pvLogPath(shiftedPath['S minus'], discountFactor)

        delta = Engine.calculateDelta(dsFdType, ds, spot, pvSpotPlus, pv, pvSpotMinus)
        gamma = Engine.calculateGamma(dsSquare, spot, pvSpotPlus, pv, pvSpotMinus)
        rho = Engine.calculateRho(drFdType, dr, option, shiftedPath, pv)
        vega = Engine.calculateVega(dvFdType, dv, option, shiftedPath, pv, discountFactor)
        theta = Engine.calculateTheta(option, shiftedPath, pv, process.dayCounter)

        return pv, delta, gamma, rho, vega, theta

    @staticmethod
    def runSingleTime(batchSize: int, option: InstrumentMC, process: Process, requestGreek: bool = False, **kwargs) -> Callable[[int], Real]:
        _coordinator = process.coordinator(option, process)
        discountFactor = _coordinator.discountFactor
        if not requestGreek:
            def calculate(seed: int):
                return Engine.calculatePV(_coordinator, discountFactor, option, batchSize, seed)
        else:
            def calculate(seed: int):
                return Engine.calculatePVWithGreek(_coordinator, discountFactor, option, batchSize, seed, process, option.spot, **kwargs)
        return calculate

    @staticmethod
    def callerJoblib(func: Callable, iterator: Sequence, **kwargs):
        func = delayed(wrap_non_picklable_objects(func))
        with Parallel(**kwargs) as p:
            res = p(func(s) for s in iterator)
        return res

    @property
    def caller(self):
        return self._caller

    @caller.setter
    def caller(self, value: Callable):
        self._caller = value

    @caller.deleter
    def caller(self):
        self._caller = None

    mostRecentEntropy = property(
        lambda self: self._mostRecentEntropy,
        lambda self, v: None, lambda self: None,
        "The entropy which is most recently used."
    )

    def __init__(self, batchSize: int, numIteration: int, caller: Optional[Callable] = None) -> None:
        """Total number of simulated paths is batchSize * numIteration."""
        self.batchSize = batchSize
        self.numIteration = numIteration
        self._mostRecentEntropy = None
        self._caller = caller

    def callerAdjust(self, entropy: int, calculate: Callable, caller: Optional[Callable] = None, callerArgs: Optional[Dict] = None):
        ss = np.random.SeedSequence(entropy)
        self._mostRecentEntropy = ss.entropy
        subs = ss.spawn(self.numIteration)
        callerArgs = dict() if callerArgs is None else callerArgs
        caller = self._caller if caller is None else caller
        if caller is None:
            callerArgs["n_jobs"] = cpu_count() if "n_jobs" not in callerArgs else callerArgs["n_jobs"]
            res = Engine.callerJoblib(calculate, subs, **callerArgs)
        else:
            res = caller(calculate, subs, **callerArgs)
        return res

    def calculate(self, option: InstrumentMC, process: Process, requestGreek: bool = False, fdStep: Optional[Dict] = None, fdType: Optional[Dict] = None, entropy: Optional[int] = None, caller: Optional[Callable] = None, callerArgs: Optional[Dict] = None) -> Union[np.ndarray, Real, Dict]:
        """
        This will trigger the calculation of NPV or Greeks.

        Parameters
        -------------

        option: InstrumentMC
            It is any instance of InstrumentMC.
        process: Process
            It is any instance of Process.
        requestGreek: bool
            It tells MCQuantLib whether to return Greeks.
        fdStep: Optional[Dict]
            it means Finite Difference Step, with default value as
            {'ds': 0.01, 'dr': 0.0001, 'dv': 0.01}. Note that ds is in log form.
        fdType: Optional[Dict]
            it means Finite Difference Type, it is a dict whose value can be
            'central', 'forward' or 'backward', it has default value as
            {'Delta': 'central', 'Rho': 'central', 'Vega': 'central'}. Note that Gamma has to
            be central.
        entropy: int
            it is the seed of random generator.
        caller: Callable
            it decides how to run simulations, especially how to parallel your CPU jobs. Tt
            takes at least two arguments which are (function, seedList), it should return a list.
        callerArgs: Dict
            it has default value as dict(n_jobs=cpu_counts).
        """

        if not requestGreek:
            _calculate = Engine.runSingleTime(self.batchSize, option, process, requestGreek)
            res = self.callerAdjust(entropy=entropy, calculate=_calculate, caller=caller, callerArgs=callerArgs)
            return np.mean(res, axis=0)
        else:
            finiteDifferenceParameter = Engine.calculateShift(fdStep, fdType)
            _calculate = Engine.runSingleTime(self.batchSize, option, process, requestGreek, **finiteDifferenceParameter)
            res = self.callerAdjust(entropy=entropy, calculate=_calculate, caller=caller, callerArgs=callerArgs)
            _pv, _delta, _gamma, _rho, _vega, _theta = np.mean(res, axis=0)
            return dict(PV=_pv, Delta=_delta, Gamma=_gamma, Rho=_rho, Vega=_vega, Theta=_theta)

    def calculateBy(self, option: InstrumentMC, process: Process, requestGreek: bool = False, fdStep: Optional[Dict] = None, fdType: Optional[Dict] = None) -> Callable[[int], Union[Real, Tuple]]:
        """It returns a function Whose parameter is a random seed and returns NPV or Greeks Dict."""
        finiteDifferenceParameter = Engine.calculateShift(fdStep, fdType) if requestGreek else dict()
        return Engine.runSingleTime(batchSize=self.batchSize, option=option, process=process, requestGreek=requestGreek, **finiteDifferenceParameter)
