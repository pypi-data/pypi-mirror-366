import numpy as np
from numbers import Real
from MCQuantLib.Instrument.VanillaOption.vanillaOption import VanillaOption
from MCQuantLib.Payoff.PlainVanillaPayoff.plainVanillaPayoff import PlainVanillaPayoff


class VanillaPutOption(VanillaOption):
    def __init__(self, spot: Real, observationDay: np.ndarray, strike: Real):
        super(VanillaPutOption, self).__init__(spot, observationDay, PlainVanillaPayoff(strike=strike, optionType=-1))

