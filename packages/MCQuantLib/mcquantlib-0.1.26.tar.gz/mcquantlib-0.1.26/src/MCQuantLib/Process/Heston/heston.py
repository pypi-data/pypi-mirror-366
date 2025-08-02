import numpy as np
import math
from scipy.stats import norm
from numba import float64
import numba as nb
import functools
from numbers import Real
from typing import Optional, Tuple, Dict, Type
from MCQuantLib.Instrument.instrument import Instrument
from MCQuantLib.Process.process import Process, ProcessMC

@nb.vectorize([float64(float64, float64, float64, float64)])
def sampleNextVByQuadraticExponential(psi, u1, m, z1):
    if psi <= 2:
        psiInv = 1 / psi
        b2 = 2 * psiInv - 1 + math.sqrt(2 * psiInv) * math.sqrt(2 * psiInv - 1)
        a = m / (1 + b2)
        return a * (math.sqrt(b2) + z1) ** 2
    else:
        p = (psi - 1) / (psi + 1)
        if u1 <= p:
            return 0
        beta = (1 - p) / m
        return math.log((1 - p) / (1 - u1)) / beta


@functools.lru_cache(maxsize=128)
def calculateKvKr(kappa, theta, volVol, dt, rho, gamma1, gamma2):
    k1 = np.e ** (-kappa * dt)
    k0 = -theta * k1
    k2 = (1 - k1) / kappa * volVol ** 2 * k1
    k3 = theta * volVol ** 2 / (2 * kappa) * (1 - k1) ** 2
    kv = [k0, k1, k2, k3]

    del k0, k1, k2, k3
    k0 = -rho * kappa * theta / volVol * dt
    k1 = gamma1 * dt * (kappa * rho / volVol - 0.5) - \
        rho / volVol
    k2 = gamma2 * dt * (kappa * rho / volVol - 0.5) + \
        rho / volVol
    k3 = gamma1 * dt * (1 - rho ** 2)
    k4 = gamma2 / gamma1 * k3
    kr = [k0, k1, k2, k3, k4]
    return kv, kr


spec = ['''
UniTuple(float64[:, :], 2)(
    float64[:], float64[:], float64, float64,
    float64, float64, float64[:, :],
    float64[:, :], float64[:, :], int32, int32
)
''']


@nb.jit(spec, nopython=True, cache=True, error_model='numpy')
def hestonJITable(kv, kr, mu, theta, v0, dt, u, zV, z, batchSize=100, gridPointInTime=100):
    v0 = np.full(batchSize, v0)
    V = np.zeros((batchSize, gridPointInTime))
    X = np.zeros(V.shape)

    vLast = v0
    xLast = np.zeros(v0.shape)
    for i in range(gridPointInTime):
        k0, k1, k2, k3 = kv
        m = theta + vLast * k1 + k0
        s2 = vLast * k2 + k3
        p = s2 / (m ** 2)
        v = sampleNextVByQuadraticExponential(p, u[:, i], m, zV[:, i])
        k0r, k1r, k2r, k3r, k4r = kr
        rt = np.sqrt(k3r * vLast + k4r * v)
        x = xLast + mu * dt + k0r + k1r * vLast + k2r * v + \
            rt * z[:, i]
        V[:, i] = v
        X[:, i] = x
        vLast, xLast = v, x

    assert V.shape == (batchSize, gridPointInTime)
    assert V.shape == X.shape
    return V, X


class Heston(Process):
    """
    A stochastic-volatility model due to Heston (1993).

    .. math::
        \\begin{align*}
        \\mathrm{d}S_t&=(r - q)S_t\\mathrm{d}t + \\sqrt{v_t} S_t \\mathrm{d}W_t \\\\
        \\mathrm{d}v_t&=\\kappa(\\theta-v_t)\\mathrm{d}t +
            \\xi \\sqrt{v_t} \\mathrm{d}Z_t
        \\end{align*}

    When passing a Heston process into the Monte Carlo engine, products will be valued
    by discounting the payoff at the risk-free (parameter *r*) rate.
    """

    def __init__(self, r: Real, q: Real, rho: Real, theta: Real, kappa: Real, xi: Real, v0Default: Real, dayCounter: Optional[int] = 252) -> None:
        """
        This will initialize the whole Heston process.

        Parameters
        ----------
        r : Real
            The risk-free rate. It is used as the continuous discount rate.
        q : Real
            The continuous yield of the underlying asset. Notice that *(r-q)* is the
            drift of the price of the underlying asset under a risk-neutral measure.
        rho : Real
            The correlation between the two standard Brownian motions. This must be
            greater than -1 and less than 1.
        theta : Real
            The long-term mean of *v*.
        kappa : Real
            The mean-reverting intensity. The larger it is, the quicker *v* reverts to
            *theta*.
        xi : Real
            The volatility of *v*.
        v0Default : Real
            The default starting value of the variance.
        dayCounter : int
            Number of days per year. This affects the discount factor.

        References
        ----------
        [1] Andersen L . Efficient Simulation of the Heston Stochastic Volatility Model[J].
        SSRN Electronic Journal, 2007, 11(3).
        """
        self.r = r
        self.q = q
        self.mu = r - q
        self.rho = rho
        self.theta = theta
        self.kappa = kappa
        self.xi = xi
        self.volVol = xi
        self.v0Default = v0Default
        self.dayCounter = dayCounter
        super(Heston, self).__init__()

    def generatePath(self, t: Real, v0: Optional[Real] = None, gamma1: Optional[Real] = 0.5, gamma2: Optional[Real] = 0.5, batchSize: Optional[int] = 100, seed: Optional[int] = None, gridPointInTime: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a set of projections.

        Parameters
        ----------
        t : Real
            The time index through which the path are generated. Note that *t=1*
            represents a 1-year horizon. Notice that *t * self.dayCounter* should be an
            integer.
        v0 : Real
            The initial value of *v*. If is None, it is set to *v0Default*. Default is
            None.
        gamma1, gamma2 : Real
            Controls the finite-difference scheme when simulating the log return. Central
            scheme corresponds to *gamma1=gamma2=0.5*.
        batchSize : int
            How many path to generate at a time.
        seed : int
            The random seed. If None, it will be chosen randomly. Default is None.
        gridPointInTime : int
            Number of grid points in time. If None, daily simulation is assumed. That is,
            length of each step in time is *1/dayCounter*. Default is None.

        Returns
        -------
        v : np.ndarray
            Projections of variance.
        x : np.ndarray
            Projections of log return.
        """
        randomGenerator = np.random.default_rng(seed)
        u = randomGenerator.uniform(0, 1, size=(batchSize, gridPointInTime))
        z = randomGenerator.normal(0, 1, size=(batchSize, gridPointInTime))
        v, x = self.generatePathGivenUZ(
            v0, t, u, z, gamma1, gamma2,
            batchSize, gridPointInTime
        )
        return v, x

    def generatePathGivenUZ(self, t: Real, u: Real, z: Real, v0: Optional[Real] = None, gamma1: Optional[Real] = 0.5, gamma2: Optional[Real] = 0.5, batchSize: Optional[int] = 100, gridPointInTime: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Project variance and log return given random numbers. *u* and *z* are
        matrices of uniform and normal variables, respectively.
        """
        v0 = self.v0Default if v0 is None else v0
        gridPointInTimeByDayCounter = int(self.dayCounter * t)
        gridPointInTime = gridPointInTimeByDayCounter if gridPointInTime is None else gridPointInTime
        # generated time grid isn't made of integers. make sure that (t*dayCounter) is an integer
        assert gridPointInTimeByDayCounter == gridPointInTime

        zV = norm.ppf(u)
        dt = t / gridPointInTime

        kv, kr = calculateKvKr(self.kappa, self.theta, self.volVol, dt, self.rho, gamma1, gamma2)
        kv = np.array(kv)
        kr = np.array(kr)
        return hestonJITable(kv, kr, self.mu, self.theta, v0, dt, u, zV, z, batchSize, gridPointInTime)

    @property
    def coordinator(self) -> Type:
        """Purely for MC compatibility."""
        return HestonMC


class HestonMC(ProcessMC):
    _cacheKey = [
        'S plus', 'S minus', 'V plus', 'V minus',
        'R plus', 'R minus', 'DF plus', 'DF minus',
        'DF next day', 'Paths next day'
    ]

    def __init__(self, option: Instrument, hst: Heston) -> None:
        self.option = option
        self.hst = hst
        self.t = option.simulatedTimeArray[-1] / hst.dayCounter
        self.discountFactor = np.exp(-hst.r * option.simulatedTimeArray[1:] / hst.dayCounter)

        self._batchSize = None
        self._pointPerPath = int(option.simulatedTimeArray[-1])
        self._pointForValuation = (option.simulatedTimeArray[1:] - 1).astype(int)
        self._CACHE = {}

    def generateEps(self, seed: int, batchSize: int) -> Tuple[np.ndarray, np.ndarray]:
        randomGenerator = np.random.default_rng(seed)
        u = randomGenerator.uniform(0, 1, (batchSize, self._pointPerPath))
        z = randomGenerator.normal(0, 1, (batchSize, self._pointPerPath))
        self._batchSize = batchSize
        return u, z

    def pathGivenEps(self, eps: Tuple) -> np.ndarray:
        u, z = eps
        path = self.hst.generatePathGivenUZ(t=self.t, u=u, z=z, v0=None, batchSize=self._batchSize)[1]
        return path[:, self._pointForValuation]

    def shift(self, path: np.ndarray, ds: Real, dr: Real, dv: Real, eps: Tuple[np.ndarray, np.ndarray]) -> Dict:
        _keyInputs = str(ds) + str(dr) + str(dv)
        try:
            valueCache = self._CACHE[_keyInputs]
        except KeyError:
            u, z = eps
            v0 = self.hst.v0Default
            r, t = self.hst.r, self.t
            q, rho, vMeanLongTerm, kappa, xi = self.hst.q, self.hst.rho, self.hst.theta, self.hst.kappa, self.hst.xi
            dayCounter = self.hst.dayCounter
            batchSize = self._batchSize
            pointForValuation = self._pointForValuation
            simulatedTimeArrayAdjust = self.option.simulatedTimeArray[1:]
            simulatedTimeArrayAdjustNextDay = self.option.simulatedTimeArray[1:] - 1
            simulatedTimeArrayAdjustScaled = simulatedTimeArrayAdjust / dayCounter
            simulatedTimeArrayAdjustNextDayScaled = simulatedTimeArrayAdjustNextDay / dayCounter

            # s shift
            sShiftPlus = np.log(1.0 + ds)
            sShiftMinus = np.log(1.0 - ds)

            # r shift
            discountFactorPlus = np.exp(-(r + dr) * simulatedTimeArrayAdjustScaled)
            discountFactorMinus = np.exp(-(r - dr) * simulatedTimeArrayAdjustScaled)
            discountFactorNextDay = np.exp(-r * simulatedTimeArrayAdjustNextDayScaled)

            # v shift. Here vega defines as: change of option price / change of long-term vol level
            hstVPlus = Heston(r=r, q=q, rho=rho, theta=vMeanLongTerm+dv, kappa=kappa, xi=xi, v0Default=v0, dayCounter=dayCounter)
            hstVMinus = Heston(r=r, q=q, rho=rho, theta=vMeanLongTerm-dv, kappa=kappa, xi=xi, v0Default=v0, dayCounter=dayCounter)
            pathVPlus = hstVPlus.generatePathGivenUZ(t=t, u=u, z=z, v0=v0, batchSize=batchSize)[1][:, pointForValuation]
            pathVMinus = hstVMinus.generatePathGivenUZ(t=t, u=u, z=z, v0=v0, batchSize=batchSize)[1][:, pointForValuation]

            # next day path
            pathNextDay = np.hstack([np.zeros((path.shape[0],1)), path[:, :-1]])

            # 缓存结果
            valueCache = dict(zip(
                self._cacheKey,
                [
                    sShiftPlus,
                    sShiftMinus,
                    pathVPlus,
                    pathVMinus,
                    dr,
                    -dr,
                    discountFactorPlus,
                    discountFactorMinus,
                    discountFactorNextDay,
                    pathNextDay
                 ]
            ))
            self._CACHE.update({_keyInputs: valueCache})
        shiftedPath = {
            'S plus': path + valueCache['S plus'],
            'S minus': path + valueCache['S minus'],
            'R plus': path + valueCache['R plus'],
            'R minus': path + valueCache['R minus'],
            'V plus': valueCache['V plus'],
            'V minus': valueCache['V minus'],
            'DF plus': valueCache['DF plus'],
            'DF minus': valueCache['DF minus'],
            'DF next day': valueCache['DF next day'],
            'Paths next day': valueCache['Paths next day'],
        }
        return shiftedPath

