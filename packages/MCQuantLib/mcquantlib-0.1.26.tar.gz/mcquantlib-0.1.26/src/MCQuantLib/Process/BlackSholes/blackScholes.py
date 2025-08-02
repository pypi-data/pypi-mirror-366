import numpy as np
from numbers import Real
from typing import Optional, Tuple, Dict, Type
from MCQuantLib.Instrument.instrument import Instrument
from MCQuantLib.Process.process import Process, ProcessMC

class BlackScholes(Process):
    """
    A Black-Scholes process. A Black-Scholes market has two securities: a
    risky asset and a risk-free bond.

    Dynamics of the asset price is driven by a geometric Brownian motion:

    .. math::

        \\mathrm{d}S_t=(r-q) S_t\\mathrm{d}t + \\sigma S_t \\mathrm{d}W_t

    and the log-return follows

    .. math::

        \\mathrm{d}\\left(\\mathrm{log}{S_t}\\right)=
        (r-q-\\frac{\\sigma^2}{2})\\mathrm{d}t+\\sigma\\mathrm{d}W_t

    where the drift (under the risk-neutral measure) is the risk-free rate.
    """

    def __init__(self, r: Real, q: Real, v: Real, dayCounter: Optional[int] = 252) -> None:
        """
        Parameters regarding market dynamics are set here before implementing
        Monte Carlo simulation.

        Parameters
        ----------
        r : Real
            The instantaneous risk-free rate.
        q : Real
            The continuous yield.
        v : Real
            The diffusion parameter.
        dayCounter : int
            An integer that controls the number of trading days in a year. Default is 252.
        """
        self.r = r / dayCounter
        self.q = q / dayCounter
        self.v = v / (dayCounter ** 0.5)
        self.dayCounter = dayCounter
        super(BlackScholes, self).__init__()

    @staticmethod
    def projectDD(drift: np.ndarray, diffusion: np.ndarray, eps: np.ndarray) -> np.ndarray:
        expDS = drift + np.multiply(eps, diffusion)
        logPath = expDS.cumsum(axis=1)
        return logPath

    def logsDriftDiffusion(self, dt: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the drift and diffusion of the logarithm of stock price.

        This function only returns array of drifts and diffusions. Along with
        which a random number generator these can generate simulated realizations
        of path of the asset price.
        """
        dt = np.array(dt)
        dt[dt < 0] = 0
        drift = (self.r - self.q - 0.5 * self.v * self.v) * dt
        diffusion = self.v * np.sqrt(dt)
        return drift, diffusion

    @property
    def coordinator(self) -> Type:
        """Purely for MC compatibility."""
        return BlackScholesMC


class BlackScholesMC(ProcessMC):
    _cacheKey = [
        'S plus', 'S minus', 'V plus', 'V minus',
        'R plus', 'R minus', 'DF plus', 'DF minus',
        'DF next day', 'Paths next day'
    ]

    def __init__(self, option: Instrument, bs: BlackScholes) -> None:
        self.option = option
        self.bs = bs

        self.t = option.simulatedTimeArray
        self.dt = np.diff(self.t)
        self.discountFactor = np.exp(-bs.r * self.t[1:])
        self.drift, self.diffusion = bs.logsDriftDiffusion(self.dt)

        self._pointsPerPath = len(self.dt)
        self._CACHE = {}

    def generateEps(self, seed: int, batchSize: int) -> np.ndarray:
        randomGenerator = np.random.default_rng(seed)
        return randomGenerator.normal(0, 1, (batchSize, self._pointsPerPath))

    def pathGivenEps(self, eps: np.ndarray) -> np.ndarray:
        return self.bs.projectDD(drift=self.drift, diffusion=self.diffusion, eps=eps)

    def shift(self, path: np.ndarray, ds: Real, dr: Real, dv: Real, eps: np.ndarray) -> Dict:
        _keyInputs = str(ds) + str(dr) + str(dv)
        try:
            valueCache = self._CACHE[_keyInputs]
        except KeyError:
            drift = self.drift
            diffusion = self.diffusion
            dayCounter = self.bs.dayCounter
            t = self.t
            dt = self.dt
            r, v = self.bs.r, self.bs.v

            sShiftPlus = np.log(1.0 + ds)
            sShiftMinus = np.log(1.0 - ds)

            rShift = dr / self.bs.dayCounter * t[1:]
            discountFactorPlus = np.exp(-(r + dr / dayCounter) * t[1:])
            discountFactorMinus = np.exp(-(r - dr / dayCounter) * t[1:])

            _sq = (dv * dv / 2) / dayCounter
            _inter = v * dv / (dayCounter ** 0.5)
            _vShiftDiffusion = dv / (dayCounter ** 0.5) * np.sqrt(dt)
            vDriftPlus = -(_sq + _inter) * dt + drift
            vDriftMinus = -(_sq - _inter) * dt + drift
            vDiffusionPlus = diffusion + _vShiftDiffusion
            vDiffusionMinus = diffusion - _vShiftDiffusion

            dtNextDay = dt.copy()
            dtNextDay[0] -= 1
            dtNextDay[dtNextDay < 0] = 0
            discountFactorNextDay = np.exp(-r * (t[1:] - 1))
            driftNextDay, diffusionNextDay = self.bs.logsDriftDiffusion(dtNextDay)
            valueCache = dict(zip(
                self._cacheKey,
                [
                    sShiftPlus, sShiftMinus,
                    (vDriftPlus, vDiffusionPlus),
                    (vDriftMinus, vDiffusionMinus),
                    rShift, -rShift, discountFactorPlus, discountFactorMinus,
                    discountFactorNextDay,
                    (driftNextDay, diffusionNextDay)
                ])
            )
            self._CACHE.update({_keyInputs: valueCache})
        shiftedPath = {
            'S plus': path + valueCache['S plus'],
            'S minus': path + valueCache['S minus'],
            'R plus': path + valueCache['R plus'],
            'R minus': path + valueCache['R minus'],
            'V plus': self.bs.projectDD(drift=valueCache['V plus'][0], diffusion=valueCache['V plus'][1], eps=eps),
            'V minus': self.bs.projectDD(drift=valueCache['V minus'][0], diffusion=valueCache['V minus'][1], eps=eps),
            'DF plus': valueCache['DF plus'],
            'DF minus': valueCache['DF minus'],
            'DF next day': valueCache['DF next day'],
            'Paths next day': self.bs.projectDD(drift=valueCache['Paths next day'][0], diffusion=valueCache['Paths next day'][1], eps=eps)
        }
        return shiftedPath

